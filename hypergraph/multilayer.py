from typing import Tuple, List, Sequence

from infomap import Infomap

from hypergraph.io import Node
from hypergraph.links import HyperLink

MultiLayerLink = Tuple[Tuple[int, int], Tuple[int, int], float]


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


def run(filename, links: Sequence[HyperLink], nodes: Sequence[Node]):
    multilayer_links = create_network(links)
    run_infomap(filename, multilayer_links, nodes)