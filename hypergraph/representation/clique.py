from itertools import combinations_with_replacement

from hypergraph.io import HyperGraph
from hypergraph.transition import w
from network import Network


def create_network(hypergraph: HyperGraph) -> Network:
    nodes, edges, weights = hypergraph

    w_ = w(edges, weights)

    links = []

    print("[clique] creating clique graph... ", end="")
    for u, v in combinations_with_replacement(nodes, 2):
        weight = w_(u, v)

        if weight < 1e-10:
            continue

        links.append((u.id, v.id, weight))

    print("done")
    return Network(nodes, links)
