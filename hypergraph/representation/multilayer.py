from itertools import product
from typing import Set, Any

from hypergraph.network import HyperGraph, MultilayerNetwork
from hypergraph.transition import p, gamma, delta, E


def create_random_walk(hypergraph: HyperGraph, self_links: bool) -> MultilayerNetwork:
    nodes, edges, weights = hypergraph

    p_ = p(edges, weights)

    links = []

    for e1, e2 in product(edges, edges):
        for u, v in product(e1.nodes, e2.nodes):
            if not self_links and u.id == v.id:
                continue

            weight = p_(e1, u, e2, v, self_links)

            if weight < 1e-10:
                continue

            links.append((e1.id, u.id, e2.id, v.id, weight))

    links = [((e1, u), (e2, v), w)
             for e1, u, e2, v, w in sorted(links)]

    return MultilayerNetwork(nodes, links)


def jaccard_index(set1: Set[Any], set2: Set[Any]) -> float:
    return len(set1 & set2) / len(set1 | set2)


def create_similarity_walk(hypergraph: HyperGraph, self_links: bool) -> MultilayerNetwork:
    nodes, edges, weights = hypergraph

    gamma_ = gamma(weights)
    delta_ = delta(weights)
    E_ = E(edges)
    edges_ = {edge.id: edge for edge in edges}

    links = []

    for e1, e2 in product(edges, edges):
        for u, v in product(e1.nodes, e2.nodes):
            if not self_links and u.id == v.id:
                continue

            if u not in e2.nodes:
                continue

            E_u = {edges_[edge] for edge in E_(u)}

            j_alpha = sum(jaccard_index(e1.nodes, beta.nodes) for beta in E_u)
            j_alpha_beta = jaccard_index(e1.nodes, e2.nodes)

            delta_e = delta_(e2) if self_links else delta_(e2) - gamma_(e2, u)

            weight = j_alpha_beta / j_alpha * gamma_(e2, v) / delta_e

            if weight < 1e-10:
                continue

            links.append((e1.id, u.id, e2.id, v.id, weight))

    links = [((e1, u), (e2, v), w)
             for e1, u, e2, v, w in sorted(links)]

    return MultilayerNetwork(nodes, links)


def create_network(hypergraph: HyperGraph, similarity_walk: bool, **kwargs) -> MultilayerNetwork:
    print("[multilayer] creating multilayer...")

    if similarity_walk:
        return create_similarity_walk(hypergraph, **kwargs)

    return create_random_walk(hypergraph, **kwargs)
