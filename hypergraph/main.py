from collections import defaultdict
from itertools import product

from infomap import Infomap

from hypergraph.parse import read, parse, Node
from hypergraph.transition import p


def create_links(edges, p):
    print("[links]: creating links... ", end="")

    for e1, e2 in product(edges, edges):
        for u, v in product(e1.nodes, e2.nodes):
            if u == v:
                continue

            w = p(u, e1, v, e2)

            if w < 1e-10:
                continue

            yield e1, u, e2, v, w

    print("done")


def create_multilayer_network(node_pairs):
    intra = []
    inter = []

    for e1, u, e2, v, w in node_pairs:
        if e1 == e2:
            links = intra
        else:
            links = inter

        # layer_id node_id layer_id node_id weight
        links.append((e1.id, u.id, e2.id, v.id, w))

    return [((e1, u), (e2, v), w)
            for links in (intra, inter)
            for e1, u, e2, v, w in sorted(links, key=lambda link: link[0])]


def create_state_network(node_pairs):
    state_ids = defaultdict(lambda: len(state_ids) + 1)

    states = set()
    links = []

    for e1, u, e2, v, w in node_pairs:
        source_id = state_ids[(e1.id, u.id)]
        target_id = state_ids[(e2.id, v.id)]

        states.add((source_id, u.id))
        states.add((target_id, v.id))

        links.append((source_id, target_id, w))

    return states, links


def create_bipartite_network(edges, nodes, node_pairs):
    bipartite_start_id = max(node.id for node in nodes) + 1

    features = [Node(bipartite_start_id + i, "Hyperedge {}".format(i + 1))
                for i in range(len(edges))]

    edge_to_feature_id = {edge.id: bipartite_start_id + i
                          for i, edge in enumerate(edges)}

    links = []

    for e1, u, e2, v, w in node_pairs:
        feature_id = edge_to_feature_id[e2.id]

        links.append((u.id, feature_id, w))
        links.append((feature_id, v.id, w))

    return bipartite_start_id, features, links


def main(file, shifted=False):
    nodes, edges, weights = parse(read(file.readlines()))

    hypergraph_links = list(create_links(edges, p(edges, weights, shifted)))

    links = create_multilayer_network(hypergraph_links)

    im = Infomap("-d -N5")
    im.set_names(nodes)
    im.add_multilayer_links(links)
    im.run()
    im.write_flow_tree("output/multilayer.ftree", states=True)

    states, links = create_state_network(node_pairs)

    im = Infomap("-d -N5")
    im.set_names(nodes)
    im.add_state_nodes(states)
    im.add_links(links)
    im.run()
    im.write_flow_tree("output/states.ftree", states=True)

    bipartite_start_id, features, links = create_bipartite_network(edges, nodes, node_pairs)

    im = Infomap("-d -N5")
    im.set_names(nodes)
    im.bipartite_start_id = bipartite_start_id - 1  # FIXME bug?
    im.add_nodes(features)
    im.add_links(links)
    im.run()
    im.write_flow_tree("output/bipartite.ftree")
