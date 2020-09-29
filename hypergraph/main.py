from functools import partial
from itertools import product

from infomap import Infomap

from hypergraph.io import read, parse
from hypergraph.transition import p


def each_node_pair(edges, nodes):
    for e1, e2 in product(edges, edges):
        for u_id, v_id in product(e1.nodes, e2.nodes):
            if u_id == v_id:
                continue

            u = next(node for node in nodes if node.id == u_id)
            v = next(node for node in nodes if node.id == v_id)

            yield e1, u, e2, v


def create_multilayer_network(edges, nodes, p):
    intra = []
    inter = []

    for e1, u, e2, v in each_node_pair(edges, nodes):
        w = p(u, e1, v, e2)

        if w < 1e-10:
            continue

        if e1 == e2:
            links = intra
        else:
            links = inter

        # layer_id node_id layer_id node_id weight
        links.append((e1.id, u.id, e2.id, v.id, w))

    links = []

    for link_type in (intra, inter):
        by_layer_id = lambda link: link[0]
        links.extend(link for link in sorted(link_type, key=by_layer_id))

    return links


def main(filename):
    with open(filename, "r") as fp:
        nodes, edges, weights = parse(read(fp.readlines()))

    P = partial(p, edges, weights, shifted=True)

    links = create_multilayer_network(edges, nodes, P)

    im = Infomap("--directed -N5")

    for node in nodes:
        im.set_name(node.id, node.name)

    for e1, u, e2, v, w in links:
        im.add_multilayer_link((e1, u), (e2, v), w)

    im.run()

    im.write_flow_tree("multilayer.ftree", states=True)


if __name__ == "__main__":
    main("data.txt")
