use crate::hypergraph::{EdgeId, HyperGraph, Node, NodeId};
use crate::network::{Link, StateNode};
use crate::preprocess::PreprocessResult;
use std::collections::HashMap;
use std::fs::File;
use std::io::BufWriter;
use std::io::Write;

pub fn create(hypergraph: HyperGraph, values: PreprocessResult) -> std::io::Result<()> {
    println!("Generating bipartite...");

    let PreprocessResult { d, gamma, pi, .. } = values;

    let bipartite_start_id = hypergraph
        .nodes
        .iter()
        .max_by_key(|node| node.id)
        .unwrap()
        .id
        + 1;

    let features: Vec<Node> = hypergraph
        .edges
        .iter()
        .enumerate()
        .map(|(i, edge)| Node {
            id: bipartite_start_id + i,
            name: format!("\"Hyperedge {}\"", edge.id),
        })
        .collect();

    let edge_id_to_feature_id: HashMap<EdgeId, NodeId> = hypergraph
        .edges
        .iter()
        .enumerate()
        .map(|(i, edge)| (edge.id, bipartite_start_id + i))
        .collect();

    let mut links = vec![];

    for edge in &hypergraph.edges {
        for node in &edge.nodes {
            let P_ue = edge.omega / d[&node];
            let P_ev = gamma[&(edge.id, *node)];

            if P_ue * P_ev < 1e-10 {
                continue;
            }

            let feature_id = edge_id_to_feature_id[&edge.id];

            links.push(Link {
                source: *node,
                target: feature_id,
                weight: pi[node] * P_ue,
            });

            links.push(Link {
                source: feature_id,
                target: *node,
                weight: P_ev,
            });
        }
    }

    let mut f = BufWriter::new(File::create("../output/bipartite.net")?);

    writeln!(f, "*Vertices")?;

    for node in hypergraph.nodes.iter().chain(&features) {
        writeln!(f, "{}", node.to_string())?;
    }

    writeln!(f, "*Bipartite {}", bipartite_start_id)?;

    for link in &links {
        writeln!(f, "{}", link.to_string())?;
    }

    println!("Generating bipartite non-backtracking...");

    let mut states: Vec<StateNode> = hypergraph
        .nodes
        .iter()
        .enumerate()
        .map(|(i, node)| StateNode {
            state_id: i,
            node_id: node.id,
        })
        .collect();

    let node_id_to_state_id: HashMap<NodeId, NodeId> = states
        .iter()
        .map(|state| (state.node_id, state.state_id))
        .collect();

    let mut last_state_id = states
        .iter()
        .max_by_key(|node| node.state_id)
        .unwrap()
        .state_id;

    let bipartite_state_start_id = last_state_id + 1;

    let mut links = vec![];

    for edge in &hypergraph.edges {
        let feature_id = edge_id_to_feature_id[&edge.id];

        let states_in_edge: Vec<_> = edge
            .nodes
            .iter()
            .map(|node| node_id_to_state_id[node])
            .collect();

        let feature_states: Vec<StateNode> = states_in_edge
            .iter()
            .enumerate()
            .map(|(i, _)| StateNode {
                state_id: last_state_id + i + 1,
                node_id: feature_id,
            })
            .collect();

        last_state_id += feature_states.len();

        states.extend(&feature_states);

        for (i, node) in edge.nodes.iter().enumerate() {
            let P_ue = edge.omega / d[&node];
            let P_ev = gamma[&(edge.id, *node)];

            if P_ue * P_ev < 1e-10 {
                continue;
            }

            let state_id = node_id_to_state_id[node];
            let target_feature_state_id = &feature_states[i].state_id;

            links.push(Link {
                source: state_id,
                target: *target_feature_state_id,
                weight: pi[node] * P_ue,
            });

            for source_feature_state in &feature_states {
                if source_feature_state.state_id != *target_feature_state_id {
                    links.push(Link {
                        source: source_feature_state.state_id,
                        target: state_id,
                        weight: P_ev,
                    });
                }
            }
        }
    }

    let mut f = BufWriter::new(File::create("../output/bipartite_non_backtracking.net")?);

    writeln!(f, "*Vertices")?;

    for node in hypergraph.nodes.iter().chain(&features) {
        writeln!(f, "{}", node.to_string())?;
    }

    writeln!(f, "*States")?;

    for state in &states {
        writeln!(f, "{}", state.to_string())?;
    }

    writeln!(f, "*Bipartite {}", bipartite_state_start_id)?;

    for link in &links {
        writeln!(f, "{}", link.to_string())?;
    }

    Ok(())
}
