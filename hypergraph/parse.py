import re
from collections import namedtuple
from typing import Dict


def read(lines):
    lines = (line.strip() for line in lines)
    lines = (line for line in lines if not line.startswith("#"))

    nodes = []
    edges = []
    weights = []

    contexts = {
        "nodes": "*vertices",
        "edges": "*hyperedges",
        "weights": "*weights"
    }

    context = None

    for line in lines:
        if line.startswith('*'):
            context = line.lower()
            continue
        elif context == contexts["nodes"]:
            nodes.append(line)
        elif context == contexts["edges"]:
            edges.append(line)
        elif context == contexts["weights"]:
            weights.append(line)

    return nodes, edges, weights


Node = namedtuple("Node", "id, name")
HyperEdge = namedtuple("HyperEdge", "id, nodes, omega")
Weight = namedtuple("Weight", "edge, node, gamma")


def parse_nodes(lines):
    nodes = {}

    for line in lines:
        m = re.match(r"(\d+) \"(.+)\"", line)
        if m:
            node_id, name = m.groups()
            node_id = int(node_id)
            nodes[node_id] = Node(node_id, name)

    return nodes


def parse_edges(lines, nodes: Dict[int, Node]):
    lines = (map(int, line.split()) for line in lines)

    return (HyperEdge(edge_id, set(nodes[node_id] for node_id in node_ids), omega)
            for edge_id, *node_ids, omega in lines)


def parse_weights(lines, nodes: Dict[int, Node]):
    lines = (map(int, line.split()) for line in lines)

    return (Weight(edge, nodes[node_id], gamma)
            for edge, node_id, gamma in lines)


def parse(data):
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

    return list(nodes.values()), list(edges), list(weights)
