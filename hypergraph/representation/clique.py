from collections import defaultdict
from itertools import combinations_with_replacement, product

from hypergraph.io import HyperGraph
from hypergraph.transition import w, p
from network import Network


def create_network(hypergraph: HyperGraph, directed: bool) -> Network:
    nodes, edges, weights = hypergraph

    if directed:
        links = defaultdict(float)

        p_ = p(edges, weights)

        print("[clique] creating clique graph... ", end="")
        for e1, e2 in product(edges, edges):
            for u, v in product(e1.nodes, e2.nodes):
                if u == v:
                    continue

                weight = p_(e1, u, e2, v)

                if weight < 1e-10:
                    continue

                links[u.id, v.id] += weight

        links = [(source, target, weight)
                 for (source, target), weight in links.items()]

        print("done")
    else:
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
