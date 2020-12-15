use crate::hypergraph::{HyperGraph, NodeId};
use std::collections::HashMap;
use std::fs::File;
use std::io::BufWriter;
use std::io::Write;

use crate::preprocess::PreprocessResult;
use itertools::*;

pub fn create(hypergraph: HyperGraph, values: PreprocessResult) -> std::io::Result<()> {
    println!("Generating unipartite with self-links...");

    let PreprocessResult {
        d,
        gamma,
        delta,
        pi,
        ..
    } = values;

    let mut links: HashMap<(NodeId, NodeId), _> = HashMap::new();

    for edge in &hypergraph.edges {
        for (u, v) in iproduct!(&edge.nodes, &edge.nodes) {
            let P_uv = edge.omega / d[u] * gamma[&(edge.id, *v)] / delta[&edge.id];

            let weight = pi[u] * P_uv;

            if weight < 1e-10 {
                continue;
            }

            *links.entry((*u, *v)).or_insert(0.0) += weight;
        }
    }

    let mut f = BufWriter::new(File::create(
        "../output/unipartite_directed_self_links.net",
    )?);

    writeln!(f, "*Vertices")?;

    for node in &hypergraph.nodes {
        writeln!(f, "{}", node.to_string())?;
    }

    writeln!(f, "*Links")?;

    for ((source, target), weight) in links {
        writeln!(f, "{} {} {}", source, target, weight)?;
    }

    // unipartite without self-links
    println!("Generating unipartite without self-links...");

    let mut links: HashMap<(NodeId, NodeId), _> = HashMap::new();

    for edge in &hypergraph.edges {
        for (u, v) in iproduct!(&edge.nodes, &edge.nodes) {
            if u == v {
                continue;
            }

            let delta_e = delta[&edge.id] - gamma[&(edge.id, *u)];
            let P_uv = edge.omega / d[u] * gamma[&(edge.id, *v)] / delta_e;

            let weight = pi[u] * P_uv;

            if weight < 1e-10 {
                continue;
            }

            *links.entry((*u, *v)).or_insert(0.0) += weight;
        }
    }

    let mut f = BufWriter::new(File::create("../output/unipartite_directed.net")?);

    writeln!(f, "*Vertices")?;

    for node in &hypergraph.nodes {
        writeln!(f, "{}", node.to_string())?;
    }

    writeln!(f, "*Links")?;

    for ((source, target), weight) in links {
        writeln!(f, "{} {} {}", source, target, weight)?;
    }

    Ok(())
}
