use crate::hypergraph::{HyperEdge, NodeId};
use crate::preprocess::NodeWeights;
use itertools::*;
use std::collections::HashMap;

#[inline]
fn kl_divergence(p: &[f64], q: &[f64]) -> f64 {
    debug_assert_eq!(p.len(), q.len());

    -p.iter()
        .zip(q.iter())
        .map(|(p_i, q_i)| {
            if *p_i > 0.0 {
                p_i * f64::log2(q_i / p_i)
            } else {
                0.0
            }
        })
        .sum::<f64>()
}

#[inline]
fn js_divergence(p: &[f64], q: &[f64]) -> f64 {
    debug_assert_eq!(p.len(), q.len());

    let mix: Vec<f64> = p
        .iter()
        .zip(q.iter())
        .map(|(p_i, q_i)| 0.5 * (p_i + q_i))
        .collect();

    let jsd = 0.5 * kl_divergence(&p, &mix) + 0.5 * kl_divergence(&q, &mix);

    debug_assert!(jsd >= 0.0, "jsd = {}", jsd);
    debug_assert!(jsd <= 1.0 + f64::EPSILON, "jsd = {}", jsd);

    jsd
}

#[inline]
fn normalize(x: &mut [f64]) {
    let sum: f64 = x.iter().sum();

    debug_assert!(sum > 0.0);

    x.iter_mut().for_each(|x_i| *x_i /= sum);
}

#[inline]
pub fn js_similarity(alpha: &HyperEdge, beta: &HyperEdge, gamma: &NodeWeights) -> f64 {
    let node_index: HashMap<NodeId, usize> = alpha
        .nodes
        .iter()
        .chain(beta.nodes.iter())
        .unique()
        .enumerate()
        .map(|(i, node_id)| (*node_id, i))
        .collect();

    let num_nodes = node_index.len();

    debug_assert_ne!(num_nodes, 0);

    let mut X = vec![vec![0.0; num_nodes]; 2];

    [&alpha, &beta].iter().enumerate().for_each(|(i, edge)| {
        edge.nodes
            .iter()
            .map(|node| (&node_index[node], node))
            .for_each(|(j, node)| X[i][*j] = gamma[&(edge.id, *node)]);
    });

    normalize(&mut X[0]);
    normalize(&mut X[1]);

    debug_assert!((X[0].iter().sum::<f64>() - 1.0).abs() < f64::EPSILON);
    debug_assert!((X[1].iter().sum::<f64>() - 1.0).abs() < f64::EPSILON);

    1.0 - js_divergence(&X[0], &X[1])
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_js_similarity() {
        let mut gamma: NodeWeights = HashMap::new();
        gamma.insert((0, 1), 1.0);
        gamma.insert((0, 2), 1.0);
        gamma.insert((0, 3), 1.0);

        let alpha = HyperEdge {
            id: 0,
            nodes: vec![1, 2],
            omega: 0.0,
        };
        let beta = HyperEdge {
            id: 0,
            nodes: vec![1, 2],
            omega: 0.0,
        };

        assert!((js_similarity(&alpha, &beta, &gamma) - 1.0).abs() < f64::EPSILON);
    }

    #[test]
    fn test_js_divergence() {
        let p = [0.5, 0.5];
        let q = [0.5, 0.5];

        assert!(js_divergence(&p, &q).abs() < f64::EPSILON);
    }
}
