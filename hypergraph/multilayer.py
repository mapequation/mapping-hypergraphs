from typing import List, Sequence

from infomap import Infomap

from hypergraph import run_infomap
from hypergraph.create_hyperlinks import HyperLink
from network import MultiLayerLink, Node, MultilayerNetwork


def create_network(nodes: Sequence[Node], links: Sequence[HyperLink]) -> MultilayerNetwork:
    intra = []
    inter = []

    print("[multilayer] creating multilayer... ", end="")
    for e1, u, e2, v, w in links:
        if e1 == e2:
            intra.append((e1.id, u.id, e2.id, v.id, w))
        else:
            inter.append((e1.id, u.id, e2.id, v.id, w))

    links_: List[MultiLayerLink] = [((e1, u), (e2, v), w)
                                    for links in (intra, inter)
                                    for e1, u, e2, v, w in sorted(links, key=lambda link: link[0])]

    print("done")
    return MultilayerNetwork(nodes, links_)


def run(filename,
        outdir,
        write_network: bool,
        no_infomap: bool,
        links: Sequence[HyperLink],
        nodes: Sequence[Node],
        self_links: bool,
        shifted: bool):
    file_ending = ""
    file_ending += "_shifted" if shifted else ""
    file_ending += "_self_links" if self_links else ""
    filename_ = "{}/{}{}".format(outdir, filename, file_ending)

    network = create_network(nodes, links)

    if write_network:
        with open(filename_ + ".net", "w") as fp:
            network.write(fp)

    if not no_infomap:
        def set_network(im: Infomap):
            im.set_names(network.nodes)
            im.add_multilayer_links(network.links)

        run_infomap(filename_ + ".ftree", set_network)
