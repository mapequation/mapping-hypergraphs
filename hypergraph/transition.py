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


def p(edges: Iterable[HyperEdge], weights: Iterable[Weight], shifted=False):
    gamma_ev = gamma(weights)
    delta_e = delta(weights)
    d_v = d(edges)

    def inner(u: Node, e1: HyperEdge, v: Node, e2: HyperEdge):
        if shifted:
            if v not in e1.nodes:
                return 0

            step_1 = gamma_ev(e1, v) / (delta_e(e1) - gamma_ev(e1, u))
            step_2 = e2.omega / d_v(v)

        else:
            if u not in e2.nodes:
                return 0

            step_1 = gamma_ev(e2, v) / (delta_e(e2) - gamma_ev(e2, u))
            step_2 = e2.omega / d_v(u)

        return step_1 * step_2

    return inner
