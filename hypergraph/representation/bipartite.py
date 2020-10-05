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

    get_state_id = defaultdict(lambda: len(get_state_id) + 1)

    states = None
    if non_backtracking:
        states = [StateNode(get_state_id[node.id], node.id) for node in nodes]

    links = defaultdict(float)

    for e1, e2 in product(edges, edges):
        for u, v in product(e1.nodes, e2.nodes):
            if non_backtracking and u == v:
                continue

            weight = p_(e1, u, e2, v)

            if weight < 1e-10:
                continue

            feature_id = edge_to_feature_id[e2.id]

            source_id = u.id
            target_id = v.id
            target_weight = weight

            if non_backtracking:
                source_id = get_state_id[u.id]
                target_id = get_state_id[v.id]

                create_feature_state = (feature_id, source_id) not in get_state_id
                feature_state_id = get_state_id[feature_id, source_id]

                if create_feature_state:
                    states.append(StateNode(feature_state_id, feature_id))

                feature_id = feature_state_id

                if len(e2.nodes) > 1:
                    target_weight = weight / (len(e2.nodes) - 1)

                for node in e2.nodes - {u, v}:
                    links[feature_id, get_state_id[node.id]] += target_weight

            links[source_id, feature_id] += weight
            links[feature_id, target_id] += target_weight

    links = [(source, target, weight)
             for (source, target), weight in sorted(links.items())]

    return BipartiteNetwork(nodes, links, features, states)
