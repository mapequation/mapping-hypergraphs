from collections import defaultdict
from itertools import product
from operator import attrgetter

from hypergraph.network import HyperGraph, StateNode, Node, BipartiteNetwork
from hypergraph.transition import p


def create_network(hypergraph: HyperGraph, non_backtracking: bool) -> BipartiteNetwork:
    nodes, edges, weights = hypergraph

    print("[bipartite] creating bipartite...")

    p_ = p(edges, weights)

    bipartite_start_id = max(map(attrgetter("id"), nodes)) + 1

    features = [Node(bipartite_start_id + i, "Hyperedge {}".format(i + 1))
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

                weight = p_(e1, u, e2, v, self_links=False)

                if weight < 1e-10:
                    continue

                source_id = get_state_id[u.id]
                target_id = get_state_id[v.id]
                feature_id = edge_to_feature_id[e2.id]

                create_feature_state = (feature_id, source_id) not in get_state_id
                feature_state_id = get_state_id[feature_id, source_id]

                if create_feature_state:
                    states.append(StateNode(feature_state_id, feature_id))

                links[source_id, feature_state_id] += weight
                links[feature_state_id, target_id] += weight

        links = [(source, target, weight)
                 for (source, target), weight in sorted(links.items())]

        return BipartiteNetwork(nodes, links, features, states)

    else:
        for e1, e2 in product(edges, edges):
            for u, v in product(e1.nodes, e2.nodes):
                weight = p_(e1, u, e2, v, self_links=True)

                if weight < 1e-10:
                    continue

                source_id = u.id
                target_id = v.id
                feature_id = edge_to_feature_id[e2.id]

                links[source_id, feature_id] += weight
                links[feature_id, target_id] += weight

        links = [(source, target, weight)
                 for (source, target), weight in sorted(links.items())]

        return BipartiteNetwork(nodes, links, features)
