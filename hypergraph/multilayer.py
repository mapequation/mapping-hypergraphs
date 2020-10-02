from typing import List, Sequence

from infomap import Infomap

from hypergraph.links import HyperLink
from hypergraph.network import MultiLayerLink, Node, MultilayerNetwork


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


def run_infomap(filename, network: MultilayerNetwork):
    print("[infomap] running infomap on multilayer network... ", end="")
    im = Infomap("-d -N5 --silent")
    im.set_names(network.nodes)
    im.add_multilayer_links(network.links)
    im.run()
    im.write_flow_tree(filename, states=True)
    print("done")
    print("[infomap] codelength {}".format(im.codelength))
    print("[infomap] num top modules {}".format(im.num_non_trivial_top_modules))


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
        run_infomap(filename_ + ".ftree", network)
