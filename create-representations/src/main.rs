#![allow(non_snake_case)]

use crate::bipartite::Bipartite;
use crate::config::{Config, Representation};
use crate::hyperedge_similarity::HyperEdgeSimilarity;
use crate::hypergraph::HyperGraph;
use crate::multilayer::Multilayer;
use crate::preprocess::Preprocess;
use crate::representation::NetworkRepresentation;
use crate::unipartite::Unipartite;
use std::error::Error;
use std::{env, process};

mod bipartite;
mod config;
mod hyperedge_similarity;
mod hypergraph;
mod js_similarity;
mod multilayer;
mod network;
mod preprocess;
mod representation;
mod unipartite;

fn run(config: Config) -> Result<(), Box<dyn Error>> {
    let Config {
        file,
        representation,
        outfile,
    } = config;

    let hypergraph = HyperGraph::new(&file);

    let preprocessed = Preprocess::run(&hypergraph);

    match representation {
        Representation::Bipartite(randomWalk) => {
            Bipartite::create(&hypergraph, &preprocessed, randomWalk, &outfile)?
        }
        Representation::Unipartite(randomWalk) => {
            Unipartite::create(&hypergraph, &preprocessed, randomWalk, &outfile)?
        }
        Representation::Multilayer(randomWalk) => {
            Multilayer::create(&hypergraph, &preprocessed, randomWalk, &outfile)?
        }
        Representation::HyperEdgeSimilarity(randomWalk) => {
            HyperEdgeSimilarity::create(&hypergraph, &preprocessed, randomWalk, &outfile)?
        }
    }

    println!("Done!");

    Ok(())
}

fn main() {
    let config = Config::new(env::args()).unwrap_or_else(|err| {
        eprintln!("Error: {}", err);
        process::exit(1);
    });

    if let Err(err) = run(config) {
        eprintln!("Error: {}", err);
        process::exit(1);
    }
}
