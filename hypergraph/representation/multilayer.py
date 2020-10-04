from itertools import product
from typing import List

from hypergraph.io import HyperGraph
from hypergraph.transition import p
from network import MultiLayerLink, MultilayerNetwork


def create_network(hypergraph: HyperGraph, self_links: bool) -> MultilayerNetwork:
    nodes, edges, weights = hypergraph

    print("[multilayer] creating multilayer...")

    p_ = p(edges, weights, self_links)

    intra = []
    inter = []

    for e1, e2 in product(edges, edges):
        for u, v in product(e1.nodes, e2.nodes):
            if not self_links and u == v:
                continue

            w = p_(e1, u, e2, v)

            if w < 1e-10:
                continue

            if e1 == e2:
                intra.append((e1.id, u.id, e2.id, v.id, w))
            else:
                inter.append((e1.id, u.id, e2.id, v.id, w))

    links: List[MultiLayerLink] = [((e1, u), (e2, v), w)
                                   for links in (intra, inter)
                                   for e1, u, e2, v, w in sorted(links, key=lambda link: link[0])]

    return MultilayerNetwork(nodes, links)
