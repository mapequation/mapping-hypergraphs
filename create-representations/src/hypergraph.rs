use std::error::Error;
use std::str::FromStr;
use std::string::ToString;

pub type NodeId = usize;
pub type EdgeId = usize;

#[derive(Clone)]
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

        let id: NodeId = split[0].parse()?;
        let name: String = String::from(split[1]);

        Ok(Self { id, name })
    }
}

#[derive(Clone)]
pub struct HyperEdge {
    pub id: EdgeId,
    pub nodes: Vec<NodeId>,
    pub omega: f64,
}

impl FromStr for HyperEdge {
    type Err = Box<dyn Error>;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        let split: Vec<&str> = s.split_whitespace().collect();

        let id: EdgeId = split.first().unwrap().parse()?;
        let omega: f64 = split.last().unwrap().parse()?;

        let nodes: Vec<NodeId> = split[1..split.len() - 1]
            .iter()
            .map(|node| node.parse().unwrap())
            .collect();

        Ok(Self { id, nodes, omega })
    }
}

#[derive(Copy, Clone)]
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
            edge: split[0].parse()?,
            node: split[1].parse()?,
            gamma: split[2].parse()?,
        })
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

        use Context::*;

        if lower.starts_with("*vertices") {
            Ok(Vertices)
        } else if lower.starts_with("*hyperedges") {
            Ok(HyperEdges)
        } else if lower.starts_with("*weights") {
            Ok(Weights)
        } else {
            Err(())
        }
    }
}

#[derive(Clone)]
pub struct HyperGraph {
    pub nodes: Vec<Node>,
    pub edges: Vec<HyperEdge>,
    pub weights: Vec<Gamma>,
}

impl HyperGraph {
    pub fn new(file: &str) -> Self {
        use Context::*;

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
                Some(Vertices) => nodes.push(line.parse().unwrap()),
                Some(HyperEdges) => edges.push(line.parse().unwrap()),
                Some(Weights) => weights.push(line.parse().unwrap()),
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
