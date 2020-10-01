from hypergraph import bipartite, multilayer
from hypergraph.io import read, parse
from hypergraph.links import create_links


def main(file, outdir="output", self_links=False, shifted=False):
    print("[main] starting... ", end="")
    args = locals()
    for key, value in args.items():
        if key == "file":
            value = value.name
        print("{}={} ".format(key, value), end="")
    print()

    nodes, edges, weights = parse(read(file.readlines()))

    hypergraph_links = list(create_links(edges, weights, self_links, shifted))

    file_ending = ""
    file_ending += "_self_links" if self_links else ""
    file_ending += "_shifted" if shifted else ""

    filename = "{}/multilayer{}.ftree".format(outdir, file_ending)
    links = multilayer.create_network(hypergraph_links)
    multilayer.run_infomap(filename, links, nodes)

    filename = "{}/bipartite{}.ftree".format(outdir, file_ending)
    features, links = bipartite.create_network(hypergraph_links, edges, nodes)
    bipartite.run_infomap(filename, links, nodes, features)
