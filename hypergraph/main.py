from hypergraph import representation
from hypergraph.io import read, parse


def main(file,
         multilayer=False,
         multilayer_self_links=False,
         bipartite=False,
         bipartite_non_backtracking=False,
         clique=False,
         **kwargs):
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
        representation.multilayer.run(hypergraph, multilayer_self_links, **kwargs)

    if bipartite or bipartite_non_backtracking:
        representation.bipartite.run(hypergraph, bipartite_non_backtracking, **kwargs)

    if clique:
        representation.clique.run(hypergraph, **kwargs)
