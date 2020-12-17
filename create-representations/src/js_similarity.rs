use crate::hypergraph::{HyperEdge, NodeId};
use crate::preprocess::NodeWeights;
use itertools::*;
use std::collections::HashMap;

#[inline]
fn kl_divergence(p: &[f64], q: &[f64]) -> f64 {
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
    assert_eq!(p.len(), q.len());

    let mix: Vec<f64> = p
        .iter()
        .zip(q.iter())
        .map(|(p_i, q_i)| 0.5 * (p_i + q_i))
        .collect();

    let jsd = 0.5 * kl_divergence(&p, &mix) + 0.5 * kl_divergence(&q, &mix);

    assert!(jsd >= 0.0);
    assert!(jsd - 1.0 < 1.0e-10);

    jsd
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

    let mut p: Vec<f64> = Vec::with_capacity(num_nodes);
    let mut q: Vec<f64> = Vec::with_capacity(num_nodes);

    p.resize(num_nodes, 0.0);
    q.resize(num_nodes, 0.0);

    for (node_id, node_index) in alpha.nodes.iter().map(|node| (node, &node_index[node])) {
        p[*node_index] = gamma[&(alpha.id, *node_id)];
    }

    for (node_id, node_index) in beta.nodes.iter().map(|node| (node, &node_index[node])) {
        q[*node_index] = gamma[&(beta.id, *node_id)];
    }

    let p_sum: f64 = p.iter().sum();
    let q_sum: f64 = q.iter().sum();

    for p_i in &mut p {
        *p_i /= p_sum;
    }

    for q_i in &mut q {
        *q_i /= q_sum;
    }

    1.0 - js_divergence(&p, &q)
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

        assert_eq!(js_similarity(&alpha, &beta, &gamma), 1.0);
    }

    #[test]
    fn test_js_divergence() {
        let p = [0.5, 0.5];
        let q = [0.5, 0.5];

        assert_eq!(js_divergence(&p, &q), 0.0);
    }
}
