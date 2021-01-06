use crate::bipartite::Bipartite;
use crate::config::{RandomWalk, Representation};
use crate::hyperedge_similarity::HyperEdgeSimilarity;
use crate::hypergraph::HyperGraph;
use crate::multilayer::Multilayer;
use crate::preprocess::PreprocessResult;
use crate::unipartite::Unipartite;

pub trait NetworkRepresentation {
    fn create(
        hypergraph: &HyperGraph,
        preprocessed: &PreprocessResult,
        random_walk: RandomWalk,
        outfile: &str,
    ) -> std::io::Result<()>
    where
        Self: Sized;
}

impl Representation {
    pub fn create(
        self,
        hypergraph: &HyperGraph,
        preprocessed: &PreprocessResult,
        outfile: &str,
    ) -> std::io::Result<()> {
        match self {
            Representation::Bipartite(random_walk) => {
                Bipartite::create(hypergraph, preprocessed, random_walk, outfile)?
            }
            Representation::Unipartite(random_walk) => {
                Unipartite::create(hypergraph, preprocessed, random_walk, outfile)?
            }
            Representation::Multilayer(random_walk) => {
                Multilayer::create(hypergraph, preprocessed, random_walk, outfile)?
            }
            Representation::HyperEdgeSimilarity(random_walk) => {
                HyperEdgeSimilarity::create(hypergraph, preprocessed, random_walk, outfile)?
            }
        }

        Ok(())
    }
}
