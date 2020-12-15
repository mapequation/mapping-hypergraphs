#![allow(non_snake_case)]

use std::error::Error;
use std::fs;
use std::thread;
use std::{env, process};

use crate::config::Config;
use crate::hypergraph::HyperGraph;
use crate::preprocess::Preprocess;

mod bipartite;
mod config;
mod hypergraph;
mod multilayer;
mod network;
mod preprocess;
mod unipartite;

fn main() -> Result<(), Box<dyn Error>> {
    let config = Config::new(env::args()).unwrap_or_else(|err| {
        eprintln!("Error: {}", err);
        process::exit(1);
    });

    let file = fs::read_to_string(&config.file).expect("Cannot open file");

    let hypergraph = HyperGraph::new(&file);

    let preprocessed = Preprocess::run(&hypergraph);

    let bipartite = thread::spawn({
        let hypergraph = hypergraph.clone();
        let preprocessed = preprocessed.clone();
        || {
            bipartite::create(hypergraph, preprocessed).unwrap();
        }
    });

    let unipartite = thread::spawn({
        let hypergraph = hypergraph.clone();
        let preprocessed = preprocessed.clone();
        || {
            unipartite::create(hypergraph, preprocessed).unwrap();
        }
    });

    let multilayer = thread::spawn(|| {
        multilayer::create(hypergraph, preprocessed).unwrap();
    });

    bipartite.join().unwrap();
    unipartite.join().unwrap();
    multilayer.join().unwrap();

    Ok(())
}
