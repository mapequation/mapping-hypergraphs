from itertools import product

from infomap import Infomap

from hypergraph.parse import read, parse, Node
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


def create_multilayer_network(node_pairs):
    intra = []
    inter = []

    print("[multilayer] creating multilayer... ", end="")
    for e1, u, e2, v, w in node_pairs:
        if e1 == e2:
            links = intra
        else:
            links = inter

        # layer_id node_id layer_id node_id weight
        links.append((e1.id, u.id, e2.id, v.id, w))

    links = [((e1, u), (e2, v), w)
             for links in (intra, inter)
             for e1, u, e2, v, w in sorted(links, key=lambda link: link[0])]

    print("done")
    return links


def create_bipartite_network(edges, nodes, node_pairs):
    print("[bipartite] creating bipartite... ", end="")
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

    print("done")
    return bipartite_start_id, features, links


def main(file, self_links=False, shifted=False):
    print("[main] starting...")
    nodes, edges, weights = parse(read(file.readlines()))

    hypergraph_links = list(create_links(edges, weights, self_links, shifted))

    links = create_multilayer_network(hypergraph_links)

    print("[infomap] running infomap on multilayer network... ", end="")
    im = Infomap("-d -N5 --silent")
    im.set_names(nodes)
    im.add_multilayer_links(links)
    im.run()
    im.write_flow_tree("output/multilayer.ftree", states=True)
    print("done")
    print("[infomap] codelength {}".format(im.codelength))

    bipartite_start_id, features, links = create_bipartite_network(edges, nodes, hypergraph_links)

    print("[infomap] running infomap on bipartite network... ", end="")
    im = Infomap("-d -N5 --silent")
    im.set_names(nodes)
    im.bipartite_start_id = bipartite_start_id - 1  # FIXME bug?
    im.add_nodes(features)
    im.add_links(links)
    im.run()
    im.write_flow_tree("output/bipartite.ftree")
    print("done")
    print("[infomap] codelength {}".format(im.codelength))
