from collections import defaultdict
from typing import Iterable

from hypergraph.parse import Node, HyperEdge, Weight


def E(edges: Iterable[HyperEdge]):
    print("[E] pre-calculating... ", end="")
    edges_ = defaultdict(list)

    for edge, nodes, _ in edges:
        for node in nodes:
            edges_[node.id].append(edge)

    edges_ = dict(edges_)
    print("done")

    def inner(v: Node, u: Node = None):
        if not u:
            return set(edges_[v.id])

        return {edge.id for edge in edges
                if {u, v} <= edge.nodes}

    return inner


def d(edges: Iterable[HyperEdge]):
    E_v = E(edges)

    def inner(v: Node):
        return sum(edge.omega for edge in edges
                   if edge.id in E_v(v))

    return inner


def delta(weights: Iterable[Weight]):
    print("[delta] pre-calculating... ", end="")
    gamma_tot = {}

    for weight in weights:
        if weight.edge not in gamma_tot:
            gamma_tot[weight.edge] = 0
        gamma_tot[weight.edge] += weight.gamma

    print("done")

    def inner(e: HyperEdge):
        return gamma_tot[e.id]

    return inner


def gamma(weights: Iterable[Weight]):
    print("[gamma] pre-calculating... ", end="")
    gamma_ = {(weight.edge, weight.node.id): weight.gamma
              for weight in weights}
    print("done")

    def inner(e: HyperEdge, v: Node):
        return gamma_[e.id, v.id]

    return inner


def step_1(weights: Iterable[Weight], self_links=False):
    gamma_ev = gamma(weights)
    delta_e = delta(weights)

    def no_self_links(e: HyperEdge, u: Node, v: Node):
        return gamma_ev(e, v) / (delta_e(e) - gamma_ev(e, u))

    def with_self_links(e: HyperEdge, u: Node, v: Node):
        return gamma_ev(e, v) / delta_e(e)

    return with_self_links if self_links else no_self_links


def step_2(edges: Iterable[HyperEdge]):
    d_v = d(edges)

    def inner(e: HyperEdge, u: Node):
        return e.omega / d_v(u)

    return inner


def p(edges: Iterable[HyperEdge], weights: Iterable[Weight], self_links=False, shifted=False):
    step_1_ = step_1(weights, self_links)
    step_2_ = step_2(edges)

    def inner(u: Node, e1: HyperEdge, v: Node, e2: HyperEdge):
        if shifted:
            if v not in e1.nodes:
                return 0

            return step_1_(e1, u, v) * step_2_(e2, v)

        else:
            if u not in e2.nodes:
                return 0

            return step_1_(e2, u, v) * step_2_(e2, u)

    return inner
