use std::fmt;
use std::string::ToString;

type NodeId = usize;
type LayerId = usize;

pub struct Link {
    pub source: NodeId,
    pub target: NodeId,
    pub weight: f64,
}

impl ToString for Link {
    fn to_string(&self) -> String {
        format!("{} {} {}", self.source, self.target, self.weight)
    }
}

#[derive(Clone)]
pub struct StateNode {
    pub state_id: NodeId,
    pub node_id: NodeId,
}

impl ToString for StateNode {
    fn to_string(&self) -> String {
        format!("{} {}", self.state_id, self.node_id)
    }
}

pub struct MultilayerLink {
    pub layer1: LayerId,
    pub source: NodeId,
    pub layer2: LayerId,
    pub target: NodeId,
    pub weight: f64,
}

impl ToString for MultilayerLink {
    fn to_string(&self) -> String {
        format!("{} {} {} {} {}", self.layer1, self.source, self.layer2, self.target, self.weight)
    }
}