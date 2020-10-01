from itertools import product

from hypergraph.transition import p


def create_links(edges, weights, self_links=False, shifted=False):
    print("[links] creating links... ")

    p_ = p(edges, weights, self_links, shifted)

    for e1, e2 in product(edges, edges):
        for u, v in product(e1.nodes, e2.nodes):
            if not self_links and u == v:
                continue

            w = p_(u, e1, v, e2)

            if w < 1e-10:
                continue

            yield e1, u, e2, v, w

    print("[links] done")
