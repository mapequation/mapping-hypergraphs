from typing import Callable, Optional

from infomap import Infomap

from hypergraph import representation
from hypergraph.io import read, parse
from network import Network

InfomapCallback = Callable[[Infomap], None]


def run_infomap(filename, callback: InfomapCallback, args=None):
    print("[infomap] running infomap... ", end="")
    im = Infomap("-N5 --silent {}".format(args if args else ""))
    callback(im)
    im.run()
    im.write_flow_tree(filename, states=True)
    print("done")
    print("[infomap] codelength {}".format(im.codelength))
    print("[infomap] num top modules {}".format(im.num_non_trivial_top_modules))


def run(file,
        outdir="output",
        multilayer=False,
        multilayer_self_links=False,
        bipartite=False,
        bipartite_non_backtracking=False,
        clique_graph=False,
        directed_clique=False,
        write_network=False,
        no_infomap=False,
        **kwargs) -> Optional[Network]:
    hypergraph = parse(read(file.readlines()))

    infomap_args = "--directed" \
        if multilayer or multilayer_self_links or bipartite or bipartite_non_backtracking or directed_clique \
        else None

    if multilayer or multilayer_self_links:
        network = representation.multilayer(hypergraph, multilayer_self_links)

        file_ending = "_self_links" if multilayer_self_links else ""
        filename = "{}/{}{}".format(outdir, "multilayer", file_ending)

        def set_network(im: Infomap):
            im.set_names(network.nodes)
            im.add_multilayer_links(network.links)

    elif bipartite or bipartite_non_backtracking:
        network = representation.bipartite(hypergraph, bipartite_non_backtracking)

        file_ending = "_non_backtracking" if bipartite_non_backtracking else "_backtracking"
        filename = "{}/{}{}".format(outdir, "bipartite", file_ending)

        def set_network(im: Infomap):
            im.set_names(network.nodes)
            im.set_names(network.features)
            im.bipartite_start_id = network.bipartite_start_id
            if network.states:
                im.add_state_nodes(network.states)
            im.add_links(network.links)

    elif clique_graph or directed_clique:
        network = representation.clique(hypergraph, directed_clique)

        file_ending = "_directed" if directed_clique else ""
        filename = "{}/{}{}".format(outdir, "clique", file_ending)

        def set_network(im: Infomap):
            im.add_nodes(network.nodes)
            im.add_links(network.links)

    else:
        return

    if write_network:
        network.write(filename + ".net")

    if not no_infomap:
        run_infomap(filename + ".ftree", set_network, infomap_args)

    return network


def main():
    from argparse import ArgumentParser, FileType, RawDescriptionHelpFormatter
    from textwrap import dedent
    import sys

    description = dedent("""
    Create maps from hypergraps with edge-dependent vertex weights.

    First, represent the hypergraph as any of
    the formats specified under "representation".

    Then, Infomap finds the community structure in the network
    representation and outputs the result in "outdir".

    For hypergraph input format, see: data/example.txt
    """)

    # noinspection PyTypeChecker
    parser = ArgumentParser(prog="hypergraph",
                            description=description,
                            formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument("file", type=FileType("r"), default=sys.stdin, help="the hypergraph file")
    parser.add_argument("outdir", nargs="?", default="output", help="directory to write output to")

    parser.add_argument("-w", "--write-network", action="store_true", help="write network representation to file")
    parser.add_argument("--no-infomap", action="store_true", help="do not run infomap")

    output = parser.add_argument_group("representation")
    options = output.add_mutually_exclusive_group(required=True)
    options.add_argument("-m", "--multilayer", action="store_true")
    options.add_argument("-M", "--multilayer-self-links", action="store_true")
    options.add_argument("-b", "--bipartite", action="store_true")
    options.add_argument("-B", "--bipartite-non-backtracking", action="store_true")
    options.add_argument("-c", "--clique-graph", action="store_true")
    options.add_argument("-C", "--directed-clique", action="store_true")

    args = parser.parse_args()

    run(**vars(args))


if __name__ == "__main__":
    main()
