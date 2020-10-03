from itertools import product
from typing import List

from infomap import Infomap

from hypergraph import run_infomap
from hypergraph.io import HyperGraph
from hypergraph.transition import p
from network import MultiLayerLink, MultilayerNetwork


def create_network(hypergraph: HyperGraph, self_links, shifted) -> MultilayerNetwork:
    nodes, edges, weights = hypergraph

    p_ = p(edges, weights, self_links, shifted)

    intra = []
    inter = []

    print("[multilayer] creating multilayer... ", end="")
    for e1, e2 in product(edges, edges):
        for u, v in product(e1.nodes, e2.nodes):
            if not self_links and u == v:
                continue

            w = p_(e1, u, e2, v)

            if w < 1e-10:
                continue

            if e1 == e2:
                intra.append((e1.id, u.id, e2.id, v.id, w))
            else:
                inter.append((e1.id, u.id, e2.id, v.id, w))

    links: List[MultiLayerLink] = [((e1, u), (e2, v), w)
                                   for links in (intra, inter)
                                   for e1, u, e2, v, w in sorted(links, key=lambda link: link[0])]

    print("done")
    return MultilayerNetwork(nodes, links)


def run(hypergraph: HyperGraph,
        filename,
        outdir,
        write_network: bool,
        no_infomap: bool,
        self_links: bool,
        shifted: bool):
    file_ending = ""
    file_ending += "_shifted" if shifted else ""
    file_ending += "_self_links" if self_links else ""
    filename_ = "{}/{}{}".format(outdir, filename, file_ending)

    network = create_network(hypergraph, self_links, shifted)

    if write_network:
        with open(filename_ + ".net", "w") as fp:
            network.write(fp)

    if not no_infomap:
        def set_network(im: Infomap):
            im.set_names(network.nodes)
            im.add_multilayer_links(network.links)

        run_infomap(filename_ + ".ftree", set_network, args="-d")
