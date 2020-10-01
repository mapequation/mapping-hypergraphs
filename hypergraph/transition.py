from collections import defaultdict
from typing import Iterable, Set

from hypergraph.io import Node, HyperEdge, Weight


def E(edges: Iterable[HyperEdge]):
    edges_ = defaultdict(set)

    for edge, nodes, _ in edges:
        for node in nodes:
            edges_[node.id].add(edge)

    edges_ = dict(edges_)

    def inner(v: Node) -> Set[int]:
        return edges_[v.id]

    return inner


def d(edges: Iterable[HyperEdge]):
    E_ = E(edges)

    def inner(v: Node) -> float:
        return sum(omega for edge, _, omega in edges
                   if edge in E_(v))

    return inner


def delta(weights: Iterable[Weight]):
    delta_ = defaultdict(float)

    for edge, _, gamma in weights:
        delta_[edge] += gamma

    delta_ = dict(delta_)

    def inner(e: HyperEdge) -> float:
        return delta_[e.id]

    return inner


def gamma(weights: Iterable[Weight]):
    gamma_ = {(edge, node.id): gamma_
              for edge, node, gamma_ in weights}

    def inner(e: HyperEdge, v: Node) -> float:
        return gamma_[e.id, v.id]

    return inner


def p(edges: Iterable[HyperEdge], weights: Iterable[Weight], self_links=False, shifted=False):
    print("[transition] pre-calculating probabilities... ", end="")
    gamma_ = gamma(weights)
    delta_ = delta(weights)
    d_ = d(edges)
    print("done")

    def p_node(e: HyperEdge, u: Node, v: Node):
        if self_links:
            return gamma_(e, v) / (delta_(e) - gamma_(e, u))

        return gamma_(e, v) / delta_(e)

    def p_edge(e: HyperEdge, u: Node):
        return e.omega / d_(u)

    def inner(u: Node, e1: HyperEdge, v: Node, e2: HyperEdge):
        if shifted:
            if v not in e1.nodes:
                return 0

            return p_node(e1, u, v) * p_edge(e2, v)

        else:
            if u not in e2.nodes:
                return 0

            return p_node(e2, u, v) * p_edge(e2, u)

    return inner
