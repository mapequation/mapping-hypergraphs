from collections import defaultdict
from itertools import combinations_with_replacement, product

from hypergraph.io import HyperGraph
from hypergraph.transition import w, p
from network import Network


def create_network(hypergraph: HyperGraph, directed: bool) -> Network:
    nodes, edges, weights = hypergraph

    print("[clique] creating clique graph...")

    if directed:
        links = defaultdict(float)

        p_ = p(edges, weights)

        for e1, e2 in product(edges, edges):
            for u, v in product(e1.nodes, e2.nodes):
                weight = p_(e1, u, e2, v)

                if weight < 1e-10:
                    continue

                links[u.id, v.id] += weight

        links = [(source, target, weight)
                 for (source, target), weight in sorted(links.items())]

    else:
        w_ = w(edges, weights)

        links = []

        for u, v in combinations_with_replacement(nodes, 2):
            weight = w_(u, v, self_links=True)

            if weight < 1e-10:
                continue

            links.append((u.id, v.id, weight))

    return Network(nodes, links)
