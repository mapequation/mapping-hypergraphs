from collections import namedtuple
from typing import Tuple

MultiLayerLink = Tuple[Tuple[int, int], Tuple[int, int], float]
Link = Tuple[int, int, float]

Node = namedtuple("Node", "id, name")
StateNode = namedtuple("StateNode", "state_id, node_id")

HyperEdge = namedtuple("HyperEdge", "id, nodes, omega")
HyperLink = Tuple[HyperEdge, Node, HyperEdge, Node, float]

Gamma = namedtuple("Gamma", "edge, node, gamma")
