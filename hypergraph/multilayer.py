from typing import List, Sequence

from infomap import Infomap

from hypergraph.io import write_multilayer_network
from hypergraph.network import MultiLayerLink, HyperLink, Node


def create_network(links: Sequence[HyperLink]) -> List[MultiLayerLink]:
    intra = []
    inter = []

    print("[multilayer] creating multilayer... ", end="")
    for e1, u, e2, v, w in links:
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


def run_infomap(filename, links: Sequence[MultiLayerLink], nodes: Sequence[Node]):
    print("[infomap] running infomap on multilayer network... ", end="")
    im = Infomap("-d -N5 --silent")
    im.set_names(nodes)
    im.add_multilayer_links(links)
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

    multilayer_links = create_network(links)

    if write_network:
        write_multilayer_network(filename_ + ".net", multilayer_links, nodes)

    if not no_infomap:
        run_infomap(filename_ + ".ftree", multilayer_links, nodes)
