from collections import defaultdict
from typing import Iterable, Set, Optional

from hypergraph.network import Node, HyperEdge, Gamma


def E(edges: Iterable[HyperEdge]):
    """
    Set of hyperedges incident to vertex v.

    .. math:: E(v) = { e \in E : v in e }

    Set of hyperedges incident to both vertices u and v.

    .. math:: E(u, v) = { e \in E : u \in e, v \in e }
    """
    edges_ = defaultdict(set)

    for edge, nodes, _ in edges:
        for node in nodes:
            edges_[node.id].add(edge)

    edges_ = dict(edges_)

    def inner(u: Node, v: Optional[Node] = None) -> Set[int]:
        if v:
            return edges_[u.id] & edges_[v.id]

        return edges_[u.id]

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


def p(edges: Iterable[HyperEdge], weights: Iterable[Gamma]):
    """
    Transition probability to go from vertex u in edge e1 to vertex v in vertex e2.

    .. math::

        p_{u,v) = \frac{ \gamma_{e_2}(v) }{ \delta(e_2) } \frac{ \omega(e_2) } { d(u) }
    """
    print("[transition] pre-calculating probabilities...")
    gamma_ = gamma(weights)
    delta_ = delta(weights)
    d_ = d(edges)

    def inner(_: HyperEdge, u: Node, e2: HyperEdge, v: Node, self_links: bool = False) -> float:
        if u not in e2.nodes:
            return 0

        delta_e = delta_(e2) if self_links else delta_(e2) - gamma_(e2, u)

        return gamma_(e2, v) / delta_e * e2.omega / d_(u)

    return inner


def w(edges: Iterable[HyperEdge], weights: Iterable[Gamma]):
    """
    Weight for going between vertex u to v in a clique graph representation
    of a hypergraph with edge-independent vertex weights.

    Assumes edge-independent vertex weights.

    .. math::

        w_{u,v} = \sum_{e \in E(u,v) } \frac{ \omega(e) \gamma(u) \gamma(v) }{ \delta(e) }
    """
    print("[transition] pre-calculating probabilities...")
    gamma_ = gamma(weights)
    delta_ = delta(weights)
    E_ = E(edges)
    edges_ = {edge.id: edge for edge in edges}

    def inner(u: Node, v: Node, self_links: bool = False) -> float:
        E_u_v = (edges_[edge_id] for edge_id in E_(u, v))

        delta_e = lambda e: delta_(e) if self_links else delta_(e) - gamma_(e, u)

        return sum(e.omega * gamma_(e, u) * gamma_(e, v) / delta_e(e)
                   for e in E_u_v)

    return inner
