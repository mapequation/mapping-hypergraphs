import re
from collections import namedtuple
from typing import Dict, List, Tuple, Mapping, Sequence

from hypergraph.network import Node

HyperEdge = namedtuple("HyperEdge", "id, nodes, omega")
Gamma = namedtuple("Gamma", "edge, node, gamma")


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
    lines = (map(int, line.split()) for line in lines)

    return [HyperEdge(edge_id, set(nodes[node_id] for node_id in node_ids), omega)
            for edge_id, *node_ids, omega in lines]


def parse_weights(lines: Sequence[str], nodes: Mapping[int, Node]) -> List[Gamma]:
    lines = (map(int, line.split()) for line in lines)

    return [Gamma(edge, nodes[node_id], gamma)
            for edge, node_id, gamma in lines]


def parse(data: Tuple[Sequence[str], Sequence[str], Sequence[str]]) \
        -> Tuple[List[Node], List[HyperEdge], List[Gamma]]:
    nodes_lines, edges_lines, weights_lines = data

    print("[parse] parsing nodes... ", end="")
    nodes = parse_nodes(nodes_lines)
    print("done")

    print("[parse] parsing edges... ", end="")
    edges = parse_edges(edges_lines, nodes)
    print("done")

    print("[parse] parsing weights... ", end="")
    weights = parse_weights(weights_lines, nodes)
    print("done")

    return list(nodes.values()), edges, weights
