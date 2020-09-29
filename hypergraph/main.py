from functools import partial
from itertools import product

from infomap import Infomap

from hypergraph.io import read_lines
from hypergraph.parse import parse
from hypergraph.prob import p


def create_multilayer_network(nodes, edges, p):
    intra = []
    inter = []

    for e1, e2 in product(edges, edges):
        for u_id, v_id in product(e1.nodes, e2.nodes):
            if u_id == v_id:
                continue

            u = next(node for node in nodes if node.id == u_id)
            v = next(node for node in nodes if node.id == v_id)

            w = p(u, e1, v, e2)

            if w < 1e-10:
                continue

            if e1 == e2:
                links = intra
            else:
                links = inter

            links.append((e1.id, u.id, e2.id, v.id, w))
            # print(e1.id, e2.id, u.name, v.name, w)

    links = []

    for link_type in (intra, inter):
        # layer_id node_id layer_id node_id weight
        by_layer_id = lambda link: link[0]
        links.extend(link for link in sorted(link_type, key=by_layer_id))

    return links


def main(filename):
    with open(filename, "r") as fp:
        data = read_lines(fp.read())

    nodes, edges, weights = parse(data)

    P = partial(p, edges, weights, shifted=True)

    links = create_multilayer_network(nodes, edges, P)

    im = Infomap("--directed -N5")

    for node in nodes:
        im.set_name(node.id, node.name)

    for e1, u, e2, v, w in links:
        im.add_multilayer_link((e1, u), (e2, v), w)

    im.run()

    im.write_flow_tree("multilayer.ftree", states=True)


if __name__ == "__main__":
    main("data.txt")
