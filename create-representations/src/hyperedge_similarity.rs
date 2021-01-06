use crate::config::RandomWalk;
use crate::hypergraph::{EdgeId, HyperEdge, HyperGraph};
use crate::js_similarity::js_similarity;
use crate::network::{LayerId, MultilayerLink};
use crate::preprocess::PreprocessResult;
use crate::representation::NetworkRepresentation;
use itertools::*;
use std::collections::HashMap;
use std::fs::File;
use std::io::BufWriter;
use std::io::Write;

pub struct HyperEdgeSimilarity;

impl NetworkRepresentation for HyperEdgeSimilarity {
    fn create(
        hypergraph: &HyperGraph,
        preprocessed: &PreprocessResult,
        random_walk: RandomWalk,
        outfile: &str,
    ) -> std::io::Result<()> {
        println!(
            "Generating {} hyperedge-similarity...",
            random_walk.to_string()
        );

        let PreprocessResult {
            E,
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

        let D: HashMap<(LayerId, LayerId), f64> = iproduct!(&hypergraph.edges, &hypergraph.edges)
            .map(|(alpha, beta)| {
                (
                    (alpha.id, beta.id),
                    js_similarity(&alpha, &beta, &gamma) * beta.omega,
                )
            })
            .collect();

        writeln!(f, "*Vertices")?;

        for node in &hypergraph.nodes {
            writeln!(f, "{}", node.to_string())?;
        }

        writeln!(f, "*Multilayer")?;

        let mut links = vec![];

        let is_non_lazy = random_walk == RandomWalk::NonLazy;

        for alpha in &hypergraph.edges {
            for u in &alpha.nodes {
                let pi_alpha_u = pi_alpha[&(alpha.id, *u)];

                let E_u: Vec<&HyperEdge> = E[u].iter().map(|e| edge_by_id[e]).collect();

                let S_alpha: f64 = E_u.iter().map(|beta| D[&(alpha.id, beta.id)]).sum();

                for beta in E_u {
                    let D_alpha_beta = D[&(alpha.id, beta.id)];

                    for v in &beta.nodes {
                        if is_non_lazy && u == v {
                            continue;
                        }

                        let delta_e = if is_non_lazy {
                            delta[&beta.id] - gamma[&(beta.id, *u)]
                        } else {
                            delta[&beta.id]
                        };

                        let P_uv = D_alpha_beta / S_alpha * gamma[&(beta.id, *v)] / delta_e;

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
