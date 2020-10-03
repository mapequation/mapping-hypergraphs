from collections import defaultdict
from typing import Iterable, Set

from hypergraph.io import HyperEdge, Gamma
from network import Node


def E(edges: Iterable[HyperEdge]):
    """
    Set of hyperedges incident to vertex v.

    .. math:: E(v) = { e \in E : v in e }
    """
    edges_ = defaultdict(set)

    for edge, nodes, _ in edges:
        for node in nodes:
            edges_[node.id].add(edge)

    edges_ = dict(edges_)

    def inner(v: Node) -> Set[int]:
        return edges_[v.id]

    return inner


def d(edges: Iterable[HyperEdge]):
    """
    Degree of vertex v.

    .. math:: d(v) = \sum_{e \in E(v)} \omega(e)
    """
    E_ = E(edges)

    def inner(v: Node) -> float:
        return sum(omega for edge, _, omega in edges
                   if edge in E_(v))

    return inner


def delta(weights: Iterable[Gamma]):
    """
    Degree of hyperedge e.

    .. math:: \delta(e) \sum_{v \in e} \gamma_e(v)
    """
    delta_ = defaultdict(float)

    for edge, _, gamma in weights:
        delta_[edge] += gamma

    delta_ = dict(delta_)

    def inner(e: HyperEdge) -> float:
        return delta_[e.id]

    return inner


def gamma(weights: Iterable[Gamma]):
    """
    Edge-(in)dependent vertex weight.

    .. math:: \gamma_e(v)
    """
    gamma_ = {(edge, node.id): gamma_
              for edge, node, gamma_ in weights}

    def inner(e: HyperEdge, v: Node) -> float:
        return gamma_[e.id, v.id]

    return inner


def p(edges: Iterable[HyperEdge], weights: Iterable[Gamma], self_links=False, shifted=False):
    """
    Transition probability to go from vertex u in edge e1 to vertex v in vertex e2.

    .. math::

        p_{u,v) = \frac{ \gamma_{e_2}(v) }{ \delta(e_2) } \frac{ \omega(e_2) } { d(u) }
    """
    print("[transition] pre-calculating probabilities... ", end="")
    gamma_ = gamma(weights)
    delta_ = delta(weights)
    d_ = d(edges)
    print("done")

    def inner(u: Node, e1: HyperEdge, v: Node, e2: HyperEdge) -> float:
        if shifted:
            if v not in e1.nodes:
                return 0

            if self_links:
                return gamma_(e1, v) / (delta_(e1) - gamma_(e1, u)) * e2.omega / d_(v)

            return gamma_(e1, v) / delta_(e1) * e2.omega / d_(v)

        else:
            if u not in e2.nodes:
                return 0

            if self_links:
                return gamma_(e2, v) / (delta_(e2) - gamma_(e2, u)) * e2.omega / d_(u)

            return gamma_(e2, v) / delta_(e2) * e2.omega / d_(u)

    return inner

