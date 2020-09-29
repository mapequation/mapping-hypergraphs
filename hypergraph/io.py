def read_lines(data):
    lines = (line.strip() for line in data.split("\n"))
    lines = (line for line in lines if not line.startswith("#"))

    vertices = []
    hyperedges = []
    weights = []

    contexts = {
        "vertices": "*vertices",
        "hyperedges": "*hyperedges",
        "weights": "*weights"
    }

    context = None

    for line in lines:
        if line.startswith('*'):
            context = line.lower()
            continue
        elif context == contexts["vertices"]:
            vertices.append(line)
        elif context == contexts["hyperedges"]:
            hyperedges.append(line)
        elif context == contexts["weights"]:
            weights.append(line)

    return vertices, hyperedges, weights
