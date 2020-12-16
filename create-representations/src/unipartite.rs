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
        randomWalk: RandomWalk,
        outfile: &str,
    ) -> std::io::Result<()> {
        println!("Generating unipartite...");

        let PreprocessResult {
            d,
            gamma,
            delta,
            pi,
            ..
        } = preprocessed;

        let mut links: HashMap<(NodeId, NodeId), _> = HashMap::new();

        use RandomWalk::*;

        for edge in &hypergraph.edges {
            for (u, v) in iproduct!(&edge.nodes, &edge.nodes) {
                if randomWalk == NonLazy && u == v {
                    continue;
                }

                let delta_e = if randomWalk == NonLazy {
                    delta[&edge.id] - gamma[&(edge.id, *u)]
                } else {
                    delta[&edge.id]
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
