from hypergraph import representation
from hypergraph.io import read, parse


def main(file,
         outdir,
         write_network=False,
         no_infomap=False,
         shifted=False,
         multilayer=False,
         multilayer_self_links=False,
         bipartite=False,
         bipartite_non_backtracking=False,
         clique=False):
    print("[main] starting...")

    print("[main] ", end="")
    args = locals()
    for key, value in args.items():
        if key == "file":
            value = value.name
        if value:
            print("{}={} ".format(key, value), end="")
    print()

    hypergraph = parse(read(file.readlines()))

    if multilayer or multilayer_self_links:
        representation.multilayer.run(hypergraph, "multilayer", outdir, write_network, no_infomap,
                                      multilayer_self_links, shifted)

    if bipartite or bipartite_non_backtracking:
        representation.bipartite.run(hypergraph, "bipartite", outdir, write_network, no_infomap,
                                     bipartite_non_backtracking)

    if clique:
        representation.clique.run(hypergraph, "clique", outdir, write_network, no_infomap)
