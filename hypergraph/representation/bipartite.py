from collections import defaultdict
from itertools import product

from hypergraph.io import HyperGraph
from hypergraph.transition import p
from network import StateNode, Node, BipartiteNetwork


def create_network(hypergraph: HyperGraph, non_backtracking: bool) -> BipartiteNetwork:
    nodes, edges, weights = hypergraph

    print("[bipartite] creating bipartite...")

    p_ = p(edges, weights)

    bipartite_start_id = max(node.id for node in nodes) + 1

    features = [Node(bipartite_start_id + i, "Hyperedge {}".format(i + 1))
                for i in range(len(edges))]

    edge_to_feature_id = {edge.id: bipartite_start_id + i
                          for i, edge in enumerate(edges)}

    states = None
    get_state_id = defaultdict(lambda: len(get_state_id) + 1)

    if non_backtracking:
        states = []

        for node in nodes:
            state_id = get_state_id[node.id]
            states.append(StateNode(state_id, node.id))

    links = []

    for e1, e2 in product(edges, edges):
        for u, v in product(e1.nodes, e2.nodes):
            if not non_backtracking and u == v:
                continue

            w = p_(e1, u, e2, v)

            if w < 1e-10:
                continue

            feature_id = edge_to_feature_id[e2.id]

            source_id = u.id
            target_id = v.id
            target_weight = w

            if non_backtracking:
                source_id = get_state_id[u.id]
                target_id = get_state_id[v.id]

                create_feature_state = (feature_id, source_id) not in get_state_id
                feature_state_id = get_state_id[feature_id, source_id]

                if create_feature_state:
                    states.append(StateNode(feature_state_id, feature_id))

                feature_id = feature_state_id

                if len(e2.nodes) > 1:
                    target_weight = w / (len(e2.nodes) - 1)

                links.extend((feature_id, get_state_id[node.id], target_weight)
                             for node in e2.nodes
                             if node not in {u, v})

            links.append((source_id, feature_id, w))
            links.append((feature_id, target_id, target_weight))

    return BipartiteNetwork(nodes, links, features, states)
