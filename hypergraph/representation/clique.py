from itertools import combinations_with_replacement

from infomap import Infomap

from hypergraph import run_infomap
from hypergraph.io import HyperGraph
from hypergraph.transition import w
from network import Network


def create_network(hypergraph: HyperGraph) -> Network:
    nodes, edges, weights = hypergraph

    w_ = w(edges, weights)

    links = []

    print("[clique] creating clique graph... ", end="")
    for u, v in combinations_with_replacement(nodes, 2):
        weight = w_(u, v)

        if weight < 1e-10:
            continue

        links.append((u.id, v.id, weight))

    print("done")
    return Network(nodes, links)


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
