from functools import partial
from typing import Iterable

from hypergraph.io import Node, HyperEdge, Weight


def E(edges: Iterable[HyperEdge], v: Node, u: Node = None):
    if not u:
        return {edge.id for edge in edges
                if v.id in edge.nodes}

    return {edge.id for edge in edges
            if {u.id, v.id} <= edge.nodes}


def d(edges: Iterable[HyperEdge], v: Node):
    E_v = partial(E, edges)

    return sum(edge.omega for edge in edges
               if edge.id in E_v(v))


def delta(weights: Iterable[Weight], e: HyperEdge):
    return sum(weight.gamma for weight in weights
               if weight.edge == e.id)


def gamma(weights: Iterable[Weight], e: HyperEdge, v: Node):
    return next((weight.gamma for weight in weights
                 if weight.edge == e.id
                 and weight.node == v.id), 0)


def p(edges: Iterable[HyperEdge],
      weights: Iterable[Weight],
      u: Node,
      e1: HyperEdge,
      v: Node,
      e2: HyperEdge,
      shifted=False):
    gamma_ev = partial(gamma, weights)
    delta_e = partial(delta, weights)
    d_v = partial(d, edges)

    if shifted:
        if v.id not in e1.nodes:
            return 0

        step_1 = gamma_ev(e1, v) / (delta_e(e1) - gamma_ev(e1, u))
        step_2 = e2.omega / d_v(v)

    else:
        if u.id not in e2.nodes:
            return 0

        step_1 = gamma_ev(e2, v) / (delta_e(e2) - gamma_ev(e2, u))
        step_2 = e2.omega / d_v(u)

    return step_1 * step_2


if __name__ == "__main__":
    nodes = [Node(id=1, name='a'),
             Node(id=2, name='b'),
             Node(id=3, name='c'),
             Node(id=4, name='d'),
             Node(id=5, name='f')]
    edges = [HyperEdge(id=1, nodes={1, 2, 3}, omega=10),
             HyperEdge(id=2, nodes={3, 4, 5}, omega=20)]
    weights = [Weight(edge=1, node=1, gamma=1),
               Weight(edge=1, node=2, gamma=1),
               Weight(edge=1, node=3, gamma=2),
               Weight(edge=2, node=3, gamma=1),
               Weight(edge=2, node=4, gamma=1),
               Weight(edge=2, node=5, gamma=2)]

    print("E")
    print(E(edges, nodes[1]))
    print(E(edges, nodes[2]))
    print(E(edges, nodes[2], nodes[3]))

    print("d")
    print(d(edges, nodes[1]))
    print(d(edges, nodes[2]))
    print(d(edges, nodes[3]))

    print("delta")
    print(delta(weights, edges[0]))
    print(delta(weights, edges[1]))

    print("gamma")
    print(gamma(weights, edges[0], nodes[0]))
    print(gamma(weights, edges[0], nodes[2]))

    print("P")
    u = nodes[1]
    e1 = edges[0]
    v = nodes[2]
    e2 = edges[1]
    print(p(edges, weights, u, e1, v, e2))
