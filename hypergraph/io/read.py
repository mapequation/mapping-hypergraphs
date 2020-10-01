from typing import List, Tuple


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
