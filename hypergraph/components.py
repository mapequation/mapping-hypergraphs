from collections import defaultdict
from itertools import combinations

import numpy as np
from scipy.sparse.csgraph import connected_components

from hypergraph.network import HyperGraph


def unipartite_projection(hypergraph: HyperGraph):
    adj = np.zeros(shape=(len(hypergraph.nodes),) * 2, dtype=int)

    id_to_index_map = defaultdict(lambda: len(id_to_index_map))

    for edge in hypergraph.edges:
        for source, target in combinations(edge.nodes, 2):
            source_id = id_to_index_map[source.id]
            target_id = id_to_index_map[target.id]
            adj[source_id, target_id] = 1
            adj[target_id, source_id] = 1

    index_to_id_map = {index: id_ for id_, index in id_to_index_map.items()}

    return adj, index_to_id_map


def largest_connected_component(hypergraph: HyperGraph) -> HyperGraph:
    adj, index_to_id_map = unipartite_projection(hypergraph)
    n_components, labels = connected_components(adj, directed=False)

    if n_components == 1:
        return hypergraph

    label_counts = defaultdict(int)

    for label in labels:
        label_counts[label] += 1

    largest_label = max(label_counts, key=label_counts.get)

    nodes_by_id = {node.id: node for node in hypergraph.nodes}

    nodes = sorted(nodes_by_id[index_to_id_map[index]]
                   for index, label in enumerate(labels)
                   if label == largest_label)

    node_ids = {node.id for node in nodes}

    edges = sorted(edge for edge in hypergraph.edges
                   if any(node.id in node_ids for node in edge.nodes))

    edge_ids = {edge.id for edge in edges}

    weights = sorted(weight for weight in hypergraph.weights
                     if weight.edge in edge_ids and weight.node.id in node_ids)

    return HyperGraph(nodes, edges, weights)
