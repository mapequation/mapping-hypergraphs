from collections import defaultdict
from itertools import product
from typing import Callable

import numpy as np
from scipy.stats import entropy
from sklearn.preprocessing import normalize

from hypergraph.network import HyperGraph, MultilayerNetwork, HyperEdge, Node
from hypergraph.transition import pi_alpha, gamma, delta, E, d


def create_random_walk(hypergraph: HyperGraph, self_links: bool) -> MultilayerNetwork:
    nodes, edges, weights = hypergraph

    gamma_ = gamma(weights)
    pi_alpha_ = pi_alpha(weights)
    delta_ = delta(weights)
    d_ = d(edges)
    E_ = E(edges)

    links = []

    for alpha, beta in product(edges, edges):
        for u, v in product(alpha.nodes, beta.nodes):
            if not self_links and u.id == v.id:
                continue

            if beta.id not in E_(u, v):
                continue

            delta_e = delta_(beta) if self_links else delta_(beta) - gamma_(beta, u)

            P_uv = beta.omega / d_(u) * gamma_(beta, v) / delta_e

            if P_uv < 1e-10:
                continue

            weight = pi_alpha_(alpha, u) * P_uv

            links.append((alpha.id, u.id, beta.id, v.id, weight))

    links = [((e1, u), (e2, v), w)
             for e1, u, e2, v, w in sorted(links)]

    return MultilayerNetwork(nodes, links)


SimilarityMetric = Callable[[HyperEdge, HyperEdge], float]


def jaccard_index(e1: HyperEdge, e2: HyperEdge) -> float:
    return len(e1.nodes & e2.nodes) / len(e1.nodes | e2.nodes)


def sorensen_coeff(e1: HyperEdge, e2: HyperEdge) -> float:
    return 2 * len(e1.nodes & e2.nodes) / (len(e1.nodes) + len(e2.nodes))


def overlap_coeff(e1: HyperEdge, e2: HyperEdge) -> float:
    return len(e1.nodes & e2.nodes) / min(len(e1.nodes), len(e2.nodes))


def make_js_similarity(gamma: Callable[[HyperEdge, Node], float]) -> SimilarityMetric:
    def js_divergence(p: np.array, q: np.array) -> float:
        mix = 0.5 * (p + q)

        jsd = 0.5 * entropy(p, mix, base=2) + 0.5 * entropy(q, mix, base=2)

        if jsd < 0 or jsd > 1:
            raise RuntimeWarning("JSD out of bounds")

        return jsd

    def js_similarity(e1: HyperEdge, e2: HyperEdge) -> float:
        num_nodes = len(set(node.id for node in e1.nodes | e2.nodes))

        j = defaultdict(lambda: len(j))

        X = np.zeros(shape=(2, num_nodes))

        for i, edge in enumerate([e1, e2]):
            for node in edge.nodes:
                X[i, j[node.id]] = gamma(edge, node)

        normalize(X, axis=1, norm="l1", copy=False)

        return 1 - js_divergence(X[0], X[1])

    return js_similarity


def create_similarity_walk(hypergraph: HyperGraph, self_links: bool) -> MultilayerNetwork:
    nodes, edges, weights = hypergraph

    gamma_ = gamma(weights)
    pi_alpha_ = pi_alpha(weights)
    delta_ = delta(weights)
    E_ = E(edges)
    edges_ = {edge.id: edge for edge in edges}

    links = []

    similarity = make_js_similarity(gamma_)

    for alpha, beta in product(edges, edges):
        for u, v in product(alpha.nodes, beta.nodes):
            if not self_links and u.id == v.id:
                continue

            if beta.id not in E_(u, v):
                continue

            E_u = {edges_[edge] for edge in E_(u)}

            S_alpha = sum(similarity(alpha, beta_) * beta_.omega for beta_ in E_u)
            D_alpha_beta = similarity(alpha, beta) * beta.omega

            delta_e = delta_(beta) if self_links else delta_(beta) - gamma_(beta, u)

            P_uv = D_alpha_beta / S_alpha * gamma_(beta, v) / delta_e

            if P_uv < 1e-10:
                continue

            weight = pi_alpha_(alpha, u) * P_uv

            links.append((alpha.id, u.id, beta.id, v.id, weight))

    links = [((e1, u), (e2, v), w)
             for e1, u, e2, v, w in sorted(links)]

    return MultilayerNetwork(nodes, links)


def create_network(hypergraph: HyperGraph, similarity_walk: bool, **kwargs) -> MultilayerNetwork:
    print("[multilayer] creating multilayer...")

    if similarity_walk:
        return create_similarity_walk(hypergraph, **kwargs)

    return create_random_walk(hypergraph, **kwargs)
