#![allow(non_snake_case, unused)]

use std::collections::{HashMap, HashSet};
use std::error::Error;
use std::fs;
use std::fs::File;
use std::io::BufWriter;
use std::io::Write;

use itertools::*;

use crate::hypergraph::{HyperEdge, HyperGraph, Node};
use crate::network::{Link, MultilayerLink, StateNode};

mod hypergraph;
mod network;

fn main() -> Result<(), Box<dyn Error>> {
    //let file = fs::read_to_string("../data/example-paper.txt")
    let file = fs::read_to_string("../data/paleo-log(omega).txt")
        .expect("Cannot open file");

    const DEFAULT_GAMMA: f64 = 1.0;

    println!("Calculating weights...");
    let hypergraph = HyperGraph::new(&file);

    type NodeId = usize;
    type EdgeId = usize;

    let mut E: HashMap<NodeId, HashSet<EdgeId>> = HashMap::new();
    let mut d: HashMap<NodeId, f64> = HashMap::new();

    for edge in &hypergraph.edges {
        for node in &edge.nodes {
            E.entry(*node).or_insert(HashSet::new()).insert(edge.id);

            *d.entry(*node).or_insert(0.0) += edge.omega;
        }
    }

    let E = E;
    let d = d;

    let mut delta: HashMap<EdgeId, f64> = HashMap::new();
    let mut gamma: HashMap<(EdgeId, NodeId), f64> = HashMap::new();

    for weight in &hypergraph.weights {
        *delta.entry(weight.edge).or_insert(0.0) += weight.gamma;

        gamma.insert((weight.edge, weight.node), weight.gamma);
    }

    let delta = delta;
    let gamma = gamma;

    let mut pi: HashMap<NodeId, f64> = HashMap::new();

    let omega: HashMap<EdgeId, f64> = hypergraph.edges.iter()
        .map(|edge| (edge.id, edge.omega))
        .collect();

    for node in &hypergraph.nodes {
        let E_u = &E[&node.id];
        let pi_u: f64 = E_u.iter()
            .fold(0.0, |tot, edge_id| {
                let omega_e = omega[&edge_id];
                let gamma_e_u = gamma.get(&(*edge_id, node.id)).unwrap_or(&DEFAULT_GAMMA);
                tot + omega_e * gamma_e_u
            });
        pi.insert(node.id, pi_u);
    }

    let pi = pi;

    let mut pi_alpha: HashMap<(EdgeId, NodeId), f64> = HashMap::new();

    for edge in &hypergraph.edges {
        let omega_e = omega[&edge.id];

        for node in &edge.nodes {
            let gamma_e_u = gamma.get(&(edge.id, *node)).unwrap_or(&DEFAULT_GAMMA);
            pi_alpha.insert((edge.id, *node), omega_e * gamma_e_u);
        }
    }

    let pi_alpha = pi_alpha;

    // bipartite
    println!("Generating bipartite...");
    let bipartite_start_id = hypergraph.nodes.iter().max_by_key(|node| node.id).unwrap().id + 1;

    let features: Vec<Node> = hypergraph.edges.iter()
        .enumerate()
        .map(|(i, edge)|
            Node {
                id: bipartite_start_id + i,
                name: format!("\"Hyperedge {}\"", edge.id),
            })
        .collect();

    let edge_id_to_feature_id: HashMap<EdgeId, NodeId> = hypergraph.edges.iter()
        .enumerate()
        .map(|(i, edge)| (edge.id, bipartite_start_id + i))
        .collect();

    let mut links = vec![];

    for edge in &hypergraph.edges {
        for node in &edge.nodes {
            let P_ue = edge.omega / d[&node];
            let P_ev = *gamma.get(&(edge.id, *node)).unwrap_or(&DEFAULT_GAMMA);

            if P_ue * P_ev < 1e-10 {
                continue;
            }

            let feature_id = edge_id_to_feature_id[&edge.id];

            links.push(Link { source: *node, target: feature_id, weight: pi[node] * P_ue });
            links.push(Link { source: feature_id, target: *node, weight: P_ev });
        }
    }

    let mut f = File::create("../output/bipartite.net")?;
    let mut f = BufWriter::new(f);

    writeln!(f, "*Vertices");

    for node in hypergraph.nodes.iter().chain(&features) {
        writeln!(f, "{}", node.to_string());
    }

    writeln!(f, "*Bipartite {}", bipartite_start_id);

    for link in &links {
        writeln!(f, "{}", link.to_string());
    }

    // bipartite non-backtracking
    println!("Generating bipartite non-backtracking...");

    let mut states: Vec<StateNode> = hypergraph.nodes.iter()
        .enumerate()
        .map(|(i, node)| StateNode { state_id: i, node_id: node.id })
        .collect();

    let node_id_to_state_id: HashMap<NodeId, NodeId> = states.iter()
        .map(|state| (state.node_id, state.state_id))
        .collect();

    let mut last_state_id = states.iter().max_by_key(|node| node.state_id).unwrap().state_id;

    let bipartite_state_start_id = last_state_id + 1;

    let mut links = vec![];

    for edge in &hypergraph.edges {
        let feature_id = edge_id_to_feature_id[&edge.id];

        let states_in_edge: Vec<_> = edge.nodes.iter()
            .map(|node| node_id_to_state_id[node])
            .collect();

        let feature_states: Vec<StateNode> = states_in_edge.iter()
            .enumerate()
            .map(|(i, state_id)| StateNode {
                state_id: last_state_id + i + 1,
                node_id: feature_id,
            })
            .collect();

        last_state_id += feature_states.len();

        states.extend(feature_states.clone());

        for (i, node) in edge.nodes.iter().enumerate() {
            let P_ue = edge.omega / d[&node];
            let P_ev = *gamma.get(&(edge.id, *node)).unwrap_or(&DEFAULT_GAMMA);

            if P_ue * P_ev < 1e-10 {
                continue;
            }

            let state_id = node_id_to_state_id[node];
            let target_feature_state_id = &feature_states[i].state_id;

            links.push(Link { source: state_id, target: *target_feature_state_id, weight: pi[node] * P_ue });

            for source_feature_state in &feature_states {
                if source_feature_state.state_id != *target_feature_state_id {
                    links.push(Link { source: source_feature_state.state_id, target: state_id, weight: P_ev });
                }
            }
        }
    }

    let mut f = File::create("../output/bipartite_non_backtracking.net").unwrap();
    let mut f = BufWriter::new(f);

    writeln!(f, "*Vertices");

    for node in hypergraph.nodes.iter().chain(&features) {
        writeln!(f, "{}", node.to_string());
    }

    writeln!(f, "*States");

    for state in &states {
        writeln!(f, "{}", state.to_string());
    }

    writeln!(f, "*Bipartite {}", bipartite_state_start_id);

    for link in &links {
        writeln!(f, "{}", link.to_string());
    }

    // unipartite self-links
    println!("Generating unipartite with self-links...");

    let mut links: HashMap<(NodeId, NodeId), _> = HashMap::new();

    let edge_by_id: HashMap<EdgeId, _> = hypergraph.edges.iter()
        .map(|edge| (edge.id, edge))
        .collect();

    for edge in &hypergraph.edges {
        for (u, v) in iproduct!(&edge.nodes, &edge.nodes) {
            let gamma_e_v = gamma.get(&(edge.id, *v)).unwrap_or(&DEFAULT_GAMMA);
            let d_u = d.get(&u).unwrap();
            let delta_e = delta.get(&edge.id).unwrap_or(&1.0);
            let P_uv = edge.omega / d_u * gamma_e_v / delta_e;

            let weight = pi[u] * P_uv;

            if weight < 1e-10 {
                continue;
            }

            *links.entry((*u, *v)).or_insert(0.0) += weight;
        }
    }

    let mut f = File::create("../output/unipartite_directed_self_links.net").unwrap();
    let mut f = BufWriter::new(f);

    writeln!(f, "*Vertices");

    for node in &hypergraph.nodes {
        writeln!(f, "{}", node.to_string());
    }

    writeln!(f, "*Links");

    for ((source, target), weight) in links {
        writeln!(f, "{} {} {}", source, target, weight);
    }

    // unipartite without self-links
    println!("Generating unipartite without self-links...");

    let mut links: HashMap<(NodeId, NodeId), _> = HashMap::new();

    let edge_by_id: HashMap<EdgeId, _> = hypergraph.edges.iter()
        .map(|edge| (edge.id, edge))
        .collect();

    for edge in &hypergraph.edges {
        for (u, v) in iproduct!(&edge.nodes, &edge.nodes) {
            if *u == *v {
                continue;
            }

            let gamma_e_v = gamma.get(&(edge.id, *v)).unwrap_or(&DEFAULT_GAMMA);
            let gamma_e_u = gamma.get(&(edge.id, *u)).unwrap_or(&DEFAULT_GAMMA);
            let d_u = d.get(&u).unwrap();
            let delta_e = delta.get(&edge.id).unwrap_or(&1.0) - gamma_e_u;
            let P_uv = edge.omega / d_u * gamma_e_v / delta_e;

            let weight = pi[u] * P_uv;

            if weight < 1e-10 {
                continue;
            }

            *links.entry((*u, *v)).or_insert(0.0) += weight;
        }
    }

    let mut f = File::create("../output/unipartite_directed.net").unwrap();
    let mut f = BufWriter::new(f);

    writeln!(f, "*Vertices");

    for node in &hypergraph.nodes {
        writeln!(f, "{}", node.to_string());
    }

    writeln!(f, "*Links");

    for ((source, target), weight) in links {
        writeln!(f, "{} {} {}", source, target, weight);
    }

    // multilayer with self-links
    println!("Generating multilayer with self-links...");

    let mut links = vec![];

    let mut f = File::create("../output/multilayer_self_links.net").unwrap();
    let mut f = BufWriter::new(f);

    writeln!(f, "*Vertices");

    for node in &hypergraph.nodes {
        writeln!(f, "{}", node.to_string());
    }

    writeln!(f, "*Multilayer");

    for (alpha, beta) in iproduct!(&hypergraph.edges, &hypergraph.edges) {
        println!("{} {}", alpha.id, beta.id);
        for (u, v) in iproduct!(&alpha.nodes, &beta.nodes) {
            let E_u_v: Vec<_> = E[u].intersection(&E[v]).collect();

            if !E_u_v.contains(&&beta.id) {
                continue;
            }

            let gamma_e_v = gamma.get(&(beta.id, *v)).unwrap_or(&DEFAULT_GAMMA);
            let d_u = d.get(&u).unwrap();
            let delta_e = delta.get(&beta.id).unwrap_or(&1.0);
            let P_uv = beta.omega / d_u * gamma_e_v / delta_e;

            let weight = pi_alpha[&(alpha.id, *u)] * P_uv;

            if weight < 1e-10 {
                continue;
            }

            links.push(MultilayerLink {
                layer1: alpha.id,
                source: *u,
                layer2: beta.id,
                target: *v,
                weight,
            });
        }
    }

    for link in links {
        writeln!(f, "{}", link.to_string());
    }

    Ok(())
}
