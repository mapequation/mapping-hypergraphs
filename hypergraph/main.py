from hypergraph import create_hyperlinks
from hypergraph.bipartite import run as run_bipartite
from hypergraph.clique import run as run_clique
from hypergraph.io import read, parse
from hypergraph.multilayer import run as run_multilayer
from hypergraph.transition import p


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

    nodes, edges, weights = parse(read(file.readlines()))

    self_links = multilayer_self_links or clique

    link_probability = p(edges, weights, self_links, shifted)

    hyperlinks = create_hyperlinks(edges, link_probability, self_links)

    if multilayer or multilayer_self_links:
        run_multilayer("multilayer", outdir, write_network, no_infomap, hyperlinks, nodes, multilayer_self_links,
                       shifted)

    if bipartite or bipartite_non_backtracking:
        run_bipartite("bipartite", outdir, write_network, no_infomap, hyperlinks, nodes, edges,
                      bipartite_non_backtracking)

    if clique:
        run_clique("clique", outdir, write_network, no_infomap, hyperlinks, nodes)
