#![allow(non_snake_case)]

use crate::config::Config;
use crate::hypergraph::HyperGraph;
use crate::preprocess::Preprocess;
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

    representation.create(&hypergraph, &Preprocess::run(&hypergraph), &outfile)?;

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
