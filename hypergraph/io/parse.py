import re
from collections import namedtuple
from typing import Dict, List, Tuple, Mapping, Sequence

from hypergraph.network import Node

HyperEdge = namedtuple("HyperEdge", "id, nodes, omega")
Gamma = namedtuple("Gamma", "edge, node, gamma")
HyperGraph = Tuple[Sequence[Node], Sequence[HyperEdge], Sequence[Gamma]]


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
              for *first, omega in map(lambda line: line.split(), lines))

    return [HyperEdge(edge_id, set(nodes[node_id] for node_id in node_ids), omega)
            for edge_id, *node_ids, omega in lines_]


def parse_weights(lines: Sequence[str], nodes: Mapping[int, Node]) -> List[Gamma]:
    lines_ = (tuple(map(int, first)) + (float(gamma),)
              for *first, gamma in map(lambda line: line.split(), lines))

    return [Gamma(edge, nodes[node_id], gamma)
            for edge, node_id, gamma in lines_]


def unit_weights(edges: Sequence[HyperEdge]):
    return [Gamma(edge.id, node, float(1))
            for edge in edges for node in edge.nodes]


def parse(data: Tuple[Sequence[str], Sequence[str], Sequence[str]]) -> HyperGraph:
    nodes_lines, edges_lines, weights_lines = data

    print("[parse] parsing nodes...")
    nodes = parse_nodes(nodes_lines)

    print("[parse] parsing edges...")
    edges = parse_edges(edges_lines, nodes)

    if len(weights_lines):
        print("[parse] parsing weights...")
        weights = parse_weights(weights_lines, nodes)
    else:
        print("[parse] no weights found, assigning unit weights...")
        weights = unit_weights(edges)

    return list(nodes.values()), edges, weights


if __name__ == "__main__":
    nodes = [
        "1 \"a\"",
        "12 \"b\"",
        "123 \"c\""
    ]
    edges = [
        "1 12 123 3.13",
        "2 1 0",
    ]
    weights = [
        "1 12 0.0",
        "1 123 1",
        "2 1 3.13"
    ]
    n = parse_nodes(nodes)
    print(n)
    e = parse_edges(edges, n)
    print(e)
    print(parse_weights(weights, n))
    print(unit_weights(e))
