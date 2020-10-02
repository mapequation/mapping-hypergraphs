from itertools import product
from typing import Iterable, List, Tuple

from hypergraph.io import HyperEdge, Gamma
from hypergraph.transition import p
from network import Node

HyperLink = Tuple[HyperEdge, Node, HyperEdge, Node, float]


def create_hyperlinks(edges: Iterable[HyperEdge],
                      weights: Iterable[Gamma],
                      self_links=False,
                      shifted=False) -> List[HyperLink]:
    print("[links] creating links... ")

    p_ = p(edges, weights, self_links, shifted)

    links = []

    for e1, e2 in product(edges, edges):
        for u, v in product(e1.nodes, e2.nodes):
            if not self_links and u == v:
                continue

            w = p_(u, e1, v, e2)

            if w < 1e-10:
                continue

            links.append((e1, u, e2, v, w))

    print("[links] done")
    return links
