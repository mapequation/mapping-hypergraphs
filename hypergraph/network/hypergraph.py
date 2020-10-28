import re
from collections import namedtuple
from dataclasses import dataclass
from operator import methodcaller
from typing import Iterable, List, Tuple, Sequence, Mapping, Dict

from .network import Node

HyperEdge = namedtuple("HyperEdge", "id, nodes, omega")
Gamma = namedtuple("Gamma", "edge, node, gamma")


@dataclass
class HyperGraph:
    """
    Format:

        *Vertices
        # id name
        1 "a"
        2 "b"
        3 "c"
        4 "d"
        5 "f"
        *Hyperedges
        # id nodes... omega
        1 1 2 3 10      # e1
        2 3 4 5 20      # e2
        *Weights # optional
        # edge node gamma
        1 1 1      # gamma_e1(a)
        1 2 1      # gamma_e1(b)
        1 3 2      # gamma_e1(c)
        2 3 1      # gamma_e2(c)
        2 4 1      # gamma_e2(d)
        2 5 2      # gamma_e2(f)
    """
    nodes: List[Node]
    edges: List[HyperEdge]
    weights: List[Gamma]

    def __iter__(self):
        return iter((self.nodes, self.edges, self.weights))

    @classmethod
    def from_iter(cls, lines: Iterable[str]):
        nodes_lines, edges_lines, weights_lines = read(lines)

        nodes = parse_nodes(nodes_lines)

        edges = parse_edges(edges_lines, nodes)

        nodes = filter_dangling(nodes, edges)

        if len(weights_lines):
            weights = parse_weights(weights_lines, nodes)

            if len(weights) < len(nodes):
                found_weights = {weight.node.id for weight in weights}
                missing_weights = set(nodes.keys()) - found_weights
                raise RuntimeError(f"Weights missing for {', '.join(map(str, missing_weights))}")
        else:
            weights = unit_weights(edges)

        return cls(list(nodes.values()), edges, weights)


def read(lines) -> Tuple[List[str], List[str], List[str]]:
    lines = (line.strip() for line in lines)
    lines = (line for line in lines if not line.startswith("#"))

    nodes = []
    edges = []
    weights = []

    context = None

    for line in lines:
        if line.startswith('*'):
            context = line.lower()
            continue
        elif context == "*vertices":
            nodes.append(line)
        elif context == "*hyperedges":
            edges.append(line)
        elif context == "*weights":
            weights.append(line)

    return nodes, edges, weights


def filter_dangling(nodes: Mapping[int, Node], edges: Sequence[HyperEdge]) -> Dict[int, Node]:
    referenced_nodes = {node.id for edge in edges for node in edge.nodes}

    return {node.id: node for node in nodes.values()
            if node.id in referenced_nodes}


def parse_nodes(lines: Sequence[str]) -> Dict[int, Node]:
    nodes = {}

    for line in lines:
        m = re.match(r"(\d+) \"(.+)\"", line)
        if m:
            node_id, name = m.groups()
            node_id = int(node_id)
            nodes[node_id] = Node(node_id, name)

    return nodes


def parse_edges(lines: Sequence[str], nodes: Mapping[int, Node]) -> List[HyperEdge]:
    lines_ = (tuple(map(int, first)) + (float(omega),)
              for *first, omega in map(methodcaller("split"), lines))

    return [HyperEdge(edge_id, frozenset(nodes[node_id] for node_id in node_ids), omega)
            for edge_id, *node_ids, omega in lines_]


def parse_weights(lines: Sequence[str], nodes: Mapping[int, Node]) -> List[Gamma]:
    lines_ = (tuple(map(int, first)) + (float(gamma),)
              for *first, gamma in map(methodcaller("split"), lines))

    return [Gamma(edge, nodes[node_id], gamma)
            for edge, node_id, gamma in lines_]


def unit_weights(edges: Sequence[HyperEdge]) -> List[Gamma]:
    return [Gamma(edge.id, node, float(1))
            for edge in edges for node in edge.nodes]
