from hypergraph import bipartite as bipartite_, multilayer as multilayer_
from hypergraph.io import read, parse
from hypergraph.links import create_links


def main(file,
         outdir,
         shifted=False,
         multilayer=False,
         multilayer_self_links=False,
         bipartite=False,
         bipartite_non_backtracking=False):
    print("[main] starting...")

    print("[main] ", end="")
    args = locals()
    for key, value in args.items():
        if key == "file":
            value = value.name
        print("{}={} ".format(key, value), end="")
    print()

    nodes, edges, weights = parse(read(file.readlines()))

    links = create_links(edges, weights, multilayer_self_links, shifted)

    if multilayer or multilayer_self_links:
        file_ending = ""
        file_ending += "_shifted" if shifted else ""
        file_ending += "_self_links" if multilayer_self_links else ""
        filename = "{}/multilayer{}.ftree".format(outdir, file_ending)

        multilayer_.run(filename, links, nodes)

    if bipartite or bipartite_non_backtracking:
        file_ending = "_non_backtracking" if bipartite_non_backtracking else "_backtracking"
        filename = "{}/bipartite{}.ftree".format(outdir, file_ending)

        bipartite_.run(filename, links, nodes, edges, bipartite_non_backtracking)
