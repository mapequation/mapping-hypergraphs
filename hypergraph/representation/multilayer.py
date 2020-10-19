from collections import defaultdict
from itertools import product, permutations
from typing import Set, Any

from hypergraph.network import HyperGraph, MultilayerNetwork
from hypergraph.transition import p, gamma, delta


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

    j_alpha = defaultdict(float)

    for edge1, edge2 in permutations(edges, 2):
        j_alpha[edge1.id] += jaccard_index(edge1.nodes, edge2.nodes)

    gamma_ = gamma(weights)
    delta_ = delta(weights)

    links = []

    for e1, e2 in product(edges, edges):
        j = jaccard_index(e1.nodes, e2.nodes) / j_alpha[e1.id]

        for u, v in product(e1.nodes, e2.nodes):
            if not self_links and u.id == v.id:
                continue

            if u not in e2.nodes:
                continue

            weight = j * gamma_(e2, v) / delta_(e2)

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
