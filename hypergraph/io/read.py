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
