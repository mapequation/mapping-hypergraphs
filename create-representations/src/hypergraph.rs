use std::convert::TryInto;
use std::error::Error;
use std::fmt;
use std::str::FromStr;
use std::string::ToString;

use itertools::FoldWhile::Continue;

pub type NodeId = usize;
pub type EdgeId = usize;

pub struct Node {
    pub id: NodeId,
    pub name: String,
}

impl ToString for Node {
    fn to_string(&self) -> String {
        format!("{} {}", self.id, self.name)
    }
}

impl FromStr for Node {
    type Err = Box<dyn Error>;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        let split: Vec<&str> = s.splitn(2, ' ').collect();

        let id: NodeId = split[0].parse::<NodeId>()?;
        let name: String = String::from(split[1]);

        Ok(Self { id, name })
    }
}

pub struct HyperEdge {
    pub id: EdgeId,
    pub nodes: Vec<NodeId>,
    pub omega: f64,
}

impl FromStr for HyperEdge {
    type Err = Box<dyn Error>;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        let split: Vec<&str> = s.split_whitespace().collect();

        let id = split.first().unwrap().parse::<EdgeId>()?;
        let omega = split.last().unwrap().parse::<f64>()?;

        let nodes: Vec<NodeId> = split[1..split.len() - 1]
            .iter()
            .map(|x| x.parse::<NodeId>().unwrap())
            .collect();

        Ok(Self { id, nodes, omega })
    }
}

pub struct Gamma {
    pub edge: EdgeId,
    pub node: NodeId,
    pub gamma: f64,
}

impl FromStr for Gamma {
    type Err = Box<dyn Error>;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        let split: Vec<&str> = s.split_whitespace().collect();

        Ok(Self {
            edge: split[0].parse::<EdgeId>()?,
            node: split[1].parse::<NodeId>()?,
            gamma: split[2].parse::<f64>()?,
        })
    }
}

impl Default for Gamma {
    fn default() -> Self {
        Self {
            edge: 0,
            node: 0,
            gamma: 1.0,
        }
    }
}

enum Context {
    Vertices,
    HyperEdges,
    Weights,
}

impl FromStr for Context {
    type Err = ();

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        let lower = s.to_lowercase();

        if lower.starts_with("*vertices") {
            Ok(Self::Vertices)
        } else if lower.starts_with("*hyperedges") {
            Ok(Self::HyperEdges)
        } else if lower.starts_with("*weights") {
            Ok(Self::Weights)
        } else {
            Err(())
        }
    }
}

pub struct HyperGraph {
    pub nodes: Vec<Node>,
    pub edges: Vec<HyperEdge>,
    pub weights: Vec<Gamma>,
}

impl HyperGraph {
    pub fn new(file: &str) -> Self {
        let mut nodes: Vec<Node> = vec![];
        let mut edges: Vec<HyperEdge> = vec![];
        let mut weights: Vec<Gamma> = vec![];

        let mut context = None;

        for line in file.lines() {
            if line.starts_with('#') {
                continue;
            }

            if line.starts_with('*') {
                context = line.parse().ok();
                continue;
            }

            match context {
                Some(Context::Vertices) => nodes.push(line.parse().unwrap()),
                Some(Context::HyperEdges) => edges.push(line.parse().unwrap()),
                Some(Context::Weights) => weights.push(line.parse().unwrap()),
                None => (),
            }
        }

        Self {
            nodes,
            edges,
            weights,
        }
    }
}
