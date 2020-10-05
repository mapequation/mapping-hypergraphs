from itertools import product

from hypergraph.io import HyperGraph
from hypergraph.transition import p
from network import MultilayerNetwork


def create_network(hypergraph: HyperGraph, self_links: bool) -> MultilayerNetwork:
    nodes, edges, weights = hypergraph

    print("[multilayer] creating multilayer...")

    p_ = p(edges, weights)

    links = []

    for e1, e2 in product(edges, edges):
        for u, v in product(e1.nodes, e2.nodes):
            if not self_links and u == v:
                continue

            weight = p_(e1, u, e2, v, self_links)

            if weight < 1e-10:
                continue

            links.append((e1.id, u.id, e2.id, v.id, weight))

    links = [((e1, u), (e2, v), w)
             for e1, u, e2, v, w in sorted(links)]

    return MultilayerNetwork(nodes, links)
