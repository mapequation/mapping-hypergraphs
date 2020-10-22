from collections import defaultdict
from itertools import product
from operator import attrgetter
from typing import Union

from hypergraph.network import HyperGraph, StateNode, Node, BipartiteNetwork, BipartiteStateNetwork
from hypergraph.transition import gamma, delta, d


def create_network(hypergraph: HyperGraph, non_backtracking: bool) -> Union[BipartiteNetwork, BipartiteStateNetwork]:
    nodes, edges, weights = hypergraph

    print("[bipartite] creating bipartite...")

    gamma_ = gamma(weights)
    delta_ = delta(weights)
    d_ = d(edges)

    bipartite_start_id = max(map(attrgetter("id"), nodes)) + 1

    features = [Node(bipartite_start_id + i, f"Hyperedge {i + 1}")
                for i in range(len(edges))]

    edge_to_feature_id = {edge.id: bipartite_start_id + i
                          for i, edge in enumerate(edges)}

    links = defaultdict(float)

    if non_backtracking:
        get_state_id = defaultdict(lambda: len(get_state_id) + 1)

        states = [StateNode(get_state_id[node.id], node.id) for node in nodes]

        for e1, e2 in product(edges, edges):
            for u, v in product(e1.nodes, e2.nodes):
                if u.id == v.id:
                    continue

                if u not in e2.nodes:
                    continue

                hyperedge_weight = e2.omega / d_(u)
                feature_weight = gamma_(e2, v) / (delta_(e2) - gamma_(e2, u))

                if hyperedge_weight * feature_weight < 1e-10:
                    continue

                source_id = get_state_id[u.id]
                target_id = get_state_id[v.id]
                feature_id = edge_to_feature_id[e2.id]

                create_feature_state = (feature_id, source_id) not in get_state_id
                feature_state_id = get_state_id[feature_id, source_id]

                if create_feature_state:
                    states.append(StateNode(feature_state_id, feature_id))

                links[source_id, feature_state_id] += hyperedge_weight
                links[feature_state_id, target_id] += feature_weight

        links = [(source, target, weight)
                 for (source, target), weight in sorted(links.items())]

        return BipartiteStateNetwork(nodes, links, states, features)

    else:
        for e1, e2 in product(edges, edges):
            for u, v in product(e1.nodes, e2.nodes):
                if u not in e2.nodes:
                    continue

                hyperedge_weight = e2.omega / d_(u)
                feature_weight = gamma_(e2, v) / delta_(e2)

                if hyperedge_weight * feature_weight < 1e-10:
                    continue

                source_id = u.id
                target_id = v.id
                feature_id = edge_to_feature_id[e2.id]

                links[source_id, feature_id] += hyperedge_weight
                links[feature_id, target_id] += feature_weight

        links = [(source, target, weight)
                 for (source, target), weight in sorted(links.items())]

        return BipartiteNetwork(nodes, links, features)
