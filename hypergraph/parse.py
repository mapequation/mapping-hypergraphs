from hypergraph.types import Node, HyperEdge, Weight


def parse_vertices(lines):
    lines = (line.split() for line in lines)

    return (Node(int(node_id), name.strip("\""))
            for node_id, name in lines)


def parse_hyperedges(lines):
    lines = (map(int, line.split()) for line in lines)

    return (HyperEdge(edge_id, set(nodes), omega)
            for edge_id, *nodes, omega in lines)


def parse_weights(lines):
    lines = (map(int, line.split()) for line in lines)

    return (Weight(edge, node, gamma)
            for edge, node, gamma in lines)


def parse(data):
    nodes_lines, hyperedges_lines, weights_lines = data

    nodes = parse_vertices(nodes_lines)
    hyperedges = parse_hyperedges(hyperedges_lines)
    weights = parse_weights(weights_lines)

    return list(nodes), list(hyperedges), list(weights)
