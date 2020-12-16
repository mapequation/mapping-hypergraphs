use crate::config::RandomWalk;
use crate::hypergraph::HyperGraph;
use crate::preprocess::PreprocessResult;

pub trait NetworkRepresentation {
    fn create(
        hypergraph: &HyperGraph,
        preprocessed: &PreprocessResult,
        randomWalk: RandomWalk,
        outfile: &str,
    ) -> std::io::Result<()>
    where
        Self: Sized;
}
