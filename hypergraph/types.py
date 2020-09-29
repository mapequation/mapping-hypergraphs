from collections import namedtuple

Node = namedtuple("Node", "id, name")
HyperEdge = namedtuple("HyperEdge", "id, nodes, omega")
Weight = namedtuple("Weight", "edge, node, gamma")