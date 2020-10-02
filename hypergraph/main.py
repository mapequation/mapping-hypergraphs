from hypergraph import bipartite as bipartite_, multilayer as multilayer_
from hypergraph import create_hyperlinks
from hypergraph.io import read, parse


def main(file,
         outdir,
         write_network=False,
         no_infomap=False,
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
        if value:
            print("{}={} ".format(key, value), end="")
    print()

    nodes, edges, weights = parse(read(file.readlines()))

    hyperlinks = create_hyperlinks(edges, weights, multilayer_self_links, shifted)

    if multilayer or multilayer_self_links:
        multilayer_.run("multilayer", outdir, write_network, no_infomap, hyperlinks, nodes, multilayer_self_links,
                        shifted)

    if bipartite or bipartite_non_backtracking:
        bipartite_.run("bipartite", outdir, write_network, no_infomap, hyperlinks, nodes, edges,
                       bipartite_non_backtracking)
