from infomap import Infomap

from hypergraph import run_infomap
from hypergraph.io import HyperGraph
from network import Network


def create_network(hypergraph: HyperGraph) -> Network:
    return Network([], [])


def run(hypergraph: HyperGraph,
        filename,
        outdir,
        write_network: bool,
        no_infomap: bool):
    filename_ = "{}/{}".format(outdir, filename)

    network = create_network(hypergraph)

    if write_network:
        with open(filename_ + ".net", "w") as fp:
            network.write(fp)

    if not no_infomap:
        def set_network(im: Infomap):
            im.add_nodes(network.nodes)
            im.add_links(network.links)

        run_infomap(filename_ + ".ftree", set_network)
