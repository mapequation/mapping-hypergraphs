from collections import namedtuple


def read_lines(data):
    lines = (line.strip() for line in data.split("\n"))
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


def parse_vertices(lines):
    lines = (line.split() for line in lines)

    return (Node(int(node_id), name.strip("\""))
            for node_id, name in lines)


def parse_edges(lines):
    lines = (map(int, line.split()) for line in lines)

    return (HyperEdge(edge_id, set(nodes), omega)
            for edge_id, *nodes, omega in lines)


def parse_weights(lines):
    lines = (map(int, line.split()) for line in lines)

    return (Weight(edge, node, gamma)
            for edge, node, gamma in lines)


def parse(data):
    nodes_lines, edges_lines, weights_lines = data

    nodes = parse_vertices(nodes_lines)
    edges = parse_edges(edges_lines)
    weights = parse_weights(weights_lines)

    return list(nodes), list(edges), list(weights)
