use crate::hypergraph::{EdgeId, HyperGraph, NodeId};
use std::collections::{HashMap, HashSet};

pub type EdgeSet = HashMap<NodeId, HashSet<EdgeId>>;
pub type NodeStrengths = HashMap<NodeId, f64>;
pub type NodeWeights = HashMap<(EdgeId, NodeId), f64>;
pub type HyperEdgeStrengths = HashMap<EdgeId, f64>;
pub type VisitRates = HashMap<NodeId, f64>;
pub type StateVisitRates = HashMap<(EdgeId, NodeId), f64>;

#[derive(Clone)]
pub struct PreprocessResult {
    pub E: EdgeSet,
    pub d: NodeStrengths,
    pub gamma: NodeWeights,
    pub delta: HyperEdgeStrengths,
    pub pi: VisitRates,
    pub pi_alpha: StateVisitRates,
}

pub struct Preprocess;

impl Preprocess {
    pub fn run(hypergraph: &HyperGraph) -> PreprocessResult {
        println!("Preprocessing...");
        let mut E: EdgeSet = HashMap::new();
        let mut d: NodeStrengths = HashMap::new();

        for edge in &hypergraph.edges {
            for node in &edge.nodes {
                E.entry(*node).or_insert_with(HashSet::new).insert(edge.id);

                *d.entry(*node).or_insert(0.0) += edge.omega;
            }
        }

        // insert disconnected nodes
        for node in &hypergraph.nodes {
            E.entry(node.id).or_insert_with(HashSet::new);

            d.entry(node.id).or_insert(0.0);
        }

        let mut delta: HyperEdgeStrengths = HashMap::new();
        let mut gamma: NodeWeights = HashMap::new();

        for weight in &hypergraph.weights {
            *delta.entry(weight.edge).or_insert(0.0) += weight.gamma;

            gamma.insert((weight.edge, weight.node), weight.gamma);
        }

        // insert missing gamma's
        const DEFAULT_GAMMA: f64 = 1.0;

        for edge in &hypergraph.edges {
            for node in &edge.nodes {
                if !gamma.contains_key(&(edge.id, *node)) {
                    *delta.entry(edge.id).or_insert(0.0) += DEFAULT_GAMMA;
                }

                gamma.entry((edge.id, *node)).or_insert(DEFAULT_GAMMA);
            }
        }

        let mut pi: VisitRates = HashMap::new();

        let omega: HashMap<EdgeId, f64> = hypergraph
            .edges
            .iter()
            .map(|edge| (edge.id, edge.omega))
            .collect();

        for node in &hypergraph.nodes {
            let pi_u: f64 = E[&node.id]
                .iter()
                .map(|edge_id| omega[&edge_id] * gamma[&(*edge_id, node.id)])
                .sum();

            pi.insert(node.id, pi_u);
        }

        let mut pi_alpha: StateVisitRates = HashMap::new();

        for edge in &hypergraph.edges {
            let omega_e = omega[&edge.id];

            for node in &edge.nodes {
                pi_alpha.insert((edge.id, *node), omega_e * gamma[&(edge.id, *node)]);
            }
        }

        PreprocessResult {
            E,
            d,
            gamma,
            delta,
            pi,
            pi_alpha,
        }
    }
}
