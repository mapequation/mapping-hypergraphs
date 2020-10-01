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

    links = create_links(edges, weights, self_links, shifted)

    file_ending = ""
    file_ending += "_self_links" if self_links else ""
    file_ending += "_shifted" if shifted else ""

    filename = "{}/multilayer{}.ftree".format(outdir, file_ending)
    multilayer.run(filename, links, nodes)

    filename = "{}/bipartite{}.ftree".format(outdir, file_ending)
    bipartite.run(filename, links, nodes, edges)
