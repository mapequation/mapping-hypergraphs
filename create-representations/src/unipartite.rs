use crate::config::RandomWalk;
use crate::hypergraph::{HyperGraph, NodeId};
use crate::preprocess::PreprocessResult;
use crate::representation::NetworkRepresentation;
use itertools::*;
use std::collections::HashMap;
use std::fs::File;
use std::io::BufWriter;
use std::io::Write;

pub struct Unipartite;

impl NetworkRepresentation for Unipartite {
    fn create(
        hypergraph: &HyperGraph,
        preprocessed: &PreprocessResult,
        random_walk: RandomWalk,
        outfile: &str,
    ) -> std::io::Result<()> {
        println!("Generating {} unipartite...", random_walk.to_string());

        let PreprocessResult {
            d,
            gamma,
            delta,
            pi,
            ..
        } = preprocessed;

        let mut links: HashMap<(NodeId, NodeId), _> = HashMap::new();

        let is_lazy = random_walk == RandomWalk::Lazy;

        for edge in &hypergraph.edges {
            for (u, v) in iproduct!(&edge.nodes, &edge.nodes) {
                if !is_lazy && u == v {
                    continue;
                }

                let delta_e = if is_lazy {
                    delta[&edge.id]
                } else {
                    delta[&edge.id] - gamma[&(edge.id, *u)]
                };

                let P_uv = edge.omega / d[u] * gamma[&(edge.id, *v)] / delta_e;

                if P_uv < 1e-10 {
                    continue;
                }

                *links.entry((*u, *v)).or_insert(0.0) += pi[u] * P_uv;
            }
        }

        let mut f = BufWriter::new(File::create(outfile)?);

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
}
