use std::error::Error;
use std::str::FromStr;
use std::string::ToString;
use std::fmt;

enum Context {
    Vertices,
    HyperEdges,
    Weights,
}

type Id = usize;

pub struct Node {
    pub id: Id,
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
        let split: Vec<&str> = s.splitn(2, " ").collect();

        let id: Id = split[0].parse::<Id>()?;
        let name: String = String::from(split[1]);

        Ok(Self { id, name })
    }
}

pub struct HyperEdge {
    pub id: Id,
    pub nodes: Vec<Id>,
    pub omega: f64,
}

impl FromStr for HyperEdge {
    type Err = Box<dyn Error>;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        let split: Vec<&str> = s.split_whitespace().collect();

        let id = split.first().unwrap().parse::<Id>()?;
        let omega = split.last().unwrap().parse::<f64>()?;

        let nodes: Vec<Id> = split[1..split.len() - 1].iter().map(|val| val.parse::<Id>().unwrap()).collect();

        Ok(Self { id, nodes, omega })
    }
}

pub struct Gamma {
    pub edge: Id,
    pub node: Id,
    pub gamma: f64,
}

impl FromStr for Gamma {
    type Err = Box<dyn Error>;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        let split: Vec<&str> = s.split_whitespace().collect();

        Ok(Self {
            edge: split[0].parse::<Id>()?,
            node: split[1].parse::<Id>()?,
            gamma: split[2].parse::<f64>()?,
        })
    }
}

impl Default for Gamma {
    fn default() -> Self {
        Self { edge: 0, node: 0, gamma: 1.0 }
    }
}

pub struct HyperGraph {
    pub nodes: Vec<Node>,
    pub edges: Vec<HyperEdge>,
    pub weights: Vec<Gamma>,
}


impl HyperGraph {
    pub fn new(file: &str) -> Self {
        let mut node_lines: Vec<String> = vec![];
        let mut edge_lines: Vec<String> = vec![];
        let mut weight_lines: Vec<String> = vec![];

        let mut context = None;

        for line in file.lines() {
            if line.starts_with("#") {
                continue;
            }

            if line.to_lowercase().starts_with("*vertices") {
                context = Some(Context::Vertices);
                continue;
            } else if line.to_lowercase().starts_with("*hyperedges") {
                context = Some(Context::HyperEdges);
                continue;
            } else if line.to_lowercase().starts_with("*weights") {
                context = Some(Context::Weights);
                continue;
            }

            if let Some(current_context) = &context {
                match current_context {
                    Context::Vertices => node_lines.push(line.into()),
                    Context::HyperEdges => edge_lines.push(line.into()),
                    Context::Weights => weight_lines.push(line.into()),
                }
            }
        }

        let nodes = node_lines.iter().map(|line| Node::from_str(line).unwrap()).collect();
        let edges = edge_lines.iter().map(|line| HyperEdge::from_str(line).unwrap()).collect();
        let weights = weight_lines.iter().map(|line| Gamma::from_str(line).unwrap()).collect();

        Self { nodes, edges, weights }
    }
}
