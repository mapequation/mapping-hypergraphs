from collections import defaultdict, namedtuple
from typing import Sequence, Tuple, List, Optional

from infomap import Infomap

from hypergraph.io import Node, HyperEdge
from hypergraph.links import HyperLink

Link = Tuple[int, int, float]
StateNode = namedtuple("StateNode", "state_id, node_id")


def create_network(links: Sequence[HyperLink],
                   nodes: Sequence[Node],
                   edges: Sequence[HyperEdge],
                   backtracking=True) \
        -> Tuple[List[Node], List[Link], Optional[List[StateNode]]]:
    print("[bipartite] creating bipartite... ", end="")
    bipartite_start_id = max(node.id for node in nodes) + 1

    features = [Node(bipartite_start_id + i, "Hyperedge {}".format(i + 1))
                for i in range(len(edges))]

    edge_to_feature_id = {edge.id: bipartite_start_id + i
                          for i, edge in enumerate(edges)}

    states = None
    get_state_id = defaultdict(lambda: len(get_state_id) + 1)

    if not backtracking:
        states = []

        for node in nodes:
            state_id = get_state_id[node.id]
            states.append(StateNode(state_id, node.id))

    links_ = []

    for e1, u, e2, v, w in links:
        feature_id = edge_to_feature_id[e2.id]

        source_id = u.id
        target_id = v.id
        target_weight = w

        if not backtracking:
            source_id = get_state_id[u.id]
            target_id = get_state_id[v.id]

            create_feature_state = (feature_id, source_id) not in get_state_id
            feature_state_id = get_state_id[feature_id, source_id]

            if create_feature_state:
                states.append(StateNode(feature_state_id, feature_id))

            feature_id = feature_state_id

            if len(e2.nodes) > 1:
                target_weight = w / (len(e2.nodes) - 1)

            links_.extend((feature_id, get_state_id[node.id], target_weight)
                          for node in e2.nodes
                          if node not in {u, v})

        links_.append((source_id, feature_id, w))
        links_.append((feature_id, target_id, target_weight))

    print("done")
    return features, links_, states


def run_infomap(filename,
                links: Sequence[Link],
                nodes: Sequence[Node],
                features: Sequence[Node],
                states: Optional[Sequence[StateNode]] = None):
    bipartite_start_id = min(node.id for node in features)

    print("[infomap] running infomap on bipartite network... ", end="")
    im = Infomap("-d -N5 --silent")
    im.set_names(nodes)
    im.set_names(features)
    im.bipartite_start_id = bipartite_start_id - 1  # FIXME Fixed in Infomap 1.2.0
    if states:
        im.add_state_nodes(states)
    im.add_links(links)
    im.run()
    im.write_flow_tree(filename, states=True)
    print("done")
    print("[infomap] codelength {}".format(im.codelength))
    print("[infomap] num top modules {}".format(im.num_non_trivial_top_modules))


def run(filename,
        links: Sequence[HyperLink],
        nodes: Sequence[Node],
        edges: Sequence[HyperEdge],
        backtracking=False):
    features, bipartite_links, states = create_network(links, nodes, edges, backtracking)
    run_infomap(filename, bipartite_links, nodes, features, states)
