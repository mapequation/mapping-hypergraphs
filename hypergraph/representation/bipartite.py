from collections import defaultdict
from operator import attrgetter
from typing import Union

from hypergraph.network import HyperGraph, StateNode, Node, BipartiteNetwork, BipartiteStateNetwork
from hypergraph.transition import gamma, d, pi


def create_network(hypergraph: HyperGraph, non_backtracking: bool) -> Union[BipartiteNetwork, BipartiteStateNetwork]:
    nodes, edges, weights = hypergraph

    print("[bipartite] creating bipartite...")

    gamma_ = gamma(weights)
    d_ = d(edges)
    pi_ = pi(edges, weights)

    bipartite_start_id = max(map(attrgetter("id"), nodes)) + 1

    features = [Node(bipartite_start_id + i, f"Hyperedge {i + 1}")
                for i in range(len(edges))]

    edge_to_feature_id = {edge.id: bipartite_start_id + i
                          for i, edge in enumerate(edges)}

    links = defaultdict(float)

    if non_backtracking:
        get_state_id = defaultdict(lambda: len(get_state_id) + 1)

        states = [StateNode(get_state_id[node.id], node.id) for node in sorted(nodes)]

        for edge in edges:
            feature_id = edge_to_feature_id[edge.id]

            state_ids = (get_state_id[node.id] for node in edge.nodes)

            feature_states = [StateNode(get_state_id[feature_id, state_id], feature_id)
                              for state_id in state_ids]

            states.extend(feature_states)

            for node in edge.nodes:
                hyperedge_weight = edge.omega
                node_weight = gamma_(edge, node)

                if hyperedge_weight * node_weight < 1e-10:
                    continue

                state_id = get_state_id[node.id]
                target_feature_state_id = get_state_id[feature_id, state_id]

                links[state_id, target_feature_state_id] = hyperedge_weight

                for source_feature_state_id, node_id in feature_states:
                    if source_feature_state_id != target_feature_state_id:
                        links[source_feature_state_id, state_id] = node_weight

        links = [(source, target, weight)
                 for (source, target), weight in sorted(links.items())]

        return BipartiteStateNetwork(nodes, links, states, features)

    else:
        for edge in edges:
            for node in edge.nodes:
                P_ue = edge.omega / d_(node)
                P_ev = gamma_(edge, node)

                if P_ue * P_ev < 1e-10:
                    continue

                feature_id = edge_to_feature_id[edge.id]

                links[node.id, feature_id] = pi_(node) * P_ue
                links[feature_id, node.id] = P_ev

        links = [(source, target, weight)
                 for (source, target), weight in sorted(links.items())]

        return BipartiteNetwork(nodes, links, features)
