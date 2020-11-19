from itertools import combinations_with_replacement, product

from hypergraph.network import HyperGraph, Network
from hypergraph.transition import w, P, pi


def create_network(hypergraph: HyperGraph, directed: bool, self_links: bool) -> Network:
    nodes, edges, weights = hypergraph

    print("[unipartite] creating unipartite...")

    if directed:
        links = []

        P_ = P(edges, weights)
        pi_ = pi(edges, weights)

        for u, v in product(nodes, repeat=2):
            weight = pi_(u) * P_(u, v, self_links)

            if weight < 1e-10:
                continue

            links.append((u.id, v.id, weight))

    else:
        w_ = w(edges, weights)

        links = []

        for u, v in combinations_with_replacement(nodes, 2):
            weight = w_(u, v, True)

            if weight < 1e-10:
                continue

            links.append((u.id, v.id, weight))

    return Network(nodes, sorted(links))
