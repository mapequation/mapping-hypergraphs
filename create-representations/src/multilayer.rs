use crate::config::RandomWalk;
use crate::hypergraph::{EdgeId, HyperGraph};
use crate::network::MultilayerLink;
use crate::preprocess::PreprocessResult;
use crate::representation::NetworkRepresentation;
use std::collections::HashMap;
use std::fs::File;
use std::io::BufWriter;
use std::io::Write;

pub struct Multilayer;

impl NetworkRepresentation for Multilayer {
    fn create(
        hypergraph: &HyperGraph,
        preprocessed: &PreprocessResult,
        random_walk: RandomWalk,
        outfile: &str,
    ) -> std::io::Result<()> {
        println!("Generating {} multilayer...", random_walk.to_string());

        let PreprocessResult {
            E,
            d,
            gamma,
            delta,
            pi_alpha,
            ..
        } = preprocessed;

        let edge_by_id: HashMap<EdgeId, _> = hypergraph
            .edges
            .iter()
            .map(|edge| (edge.id, edge))
            .collect();

        let mut f = BufWriter::new(File::create(outfile)?);

        writeln!(f, "*Vertices")?;

        for node in &hypergraph.nodes {
            writeln!(f, "{}", node.to_string())?;
        }

        writeln!(f, "*Multilayer")?;

        let mut links = vec![];

        let is_lazy = random_walk == RandomWalk::Lazy;

        for alpha in &hypergraph.edges {
            for u in &alpha.nodes {
                let d_u = d[u];
                let pi_alpha_u = pi_alpha[&(alpha.id, *u)];

                for beta in E[u].iter().map(|e| edge_by_id[e]) {
                    for v in &beta.nodes {
                        if !is_lazy && u == v {
                            continue;
                        }

                        let delta_e = if is_lazy {
                            delta[&beta.id]
                        } else {
                            delta[&beta.id] - gamma[&(beta.id, *u)]
                        };

                        let P_uv = beta.omega / d_u * gamma[&(beta.id, *v)] / delta_e;

                        if P_uv < 1e-10 {
                            continue;
                        }

                        links.push(MultilayerLink {
                            layer1: alpha.id,
                            source: *u,
                            layer2: beta.id,
                            target: *v,
                            weight: pi_alpha_u * P_uv,
                        });
                    }
                }
            }

            for link in &links {
                writeln!(f, "{}", link.to_string())?;
            }

            links.clear();
        }

        Ok(())
    }
}
