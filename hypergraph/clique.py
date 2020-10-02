from typing import Sequence

from infomap import Infomap

from hypergraph import run_infomap
from hypergraph.create_hyperlinks import HyperLink
from network import Network, Node


def create_network(nodes: Sequence[Node], links: Sequence[HyperLink]) -> Network:
    return Network([], [])


def run(filename,
        outdir,
        write_network: bool,
        no_infomap: bool,
        links: Sequence[HyperLink],
        nodes: Sequence[Node]):
    filename_ = "{}/{}".format(outdir, filename)

    network = create_network(nodes, links)

    if write_network:
        with open(filename_ + ".net", "w") as fp:
            network.write(fp)

    if not no_infomap:
        def set_network(im: Infomap):
            im.add_nodes(network.nodes)
            im.add_links(network.links)

        run_infomap(filename_ + ".ftree", set_network)
