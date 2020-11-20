from os import path
from typing import Optional

from infomap import Infomap

from hypergraph import representation
from hypergraph.components import largest_connected_component
from hypergraph.network import HyperGraph, Network, remove_simple_hyperedges

_DEFAULT_SEED = 123
_DEFAULT_TELEPORTATION_PROB = 0.15


def run_infomap(basename: str,
                outdir: str,
                network: Network,
                args: Optional[str] = None,
                directed: bool = True,
                self_links: bool = False,
                no_infomap: bool = False,
                two_level: bool = False,
                seed: int = _DEFAULT_SEED,
                teleportation_probability: float = _DEFAULT_TELEPORTATION_PROB,
                **_):
    if no_infomap:
        return

    filename = basename + (f"_seed_{seed}" if seed != _DEFAULT_SEED else "")

    default_args = " --num-trials 20 --silent -o states"
    default_args += " --directed" if directed else ""
    default_args += " --include-self-links" if self_links else ""
    default_args += " --two-level" if two_level else ""
    default_args += f" --seed {seed}"
    default_args += f" --teleportation-probability {teleportation_probability}"
    default_args += f" --out-name {filename} "
    default_args += outdir

    print("[infomap] running infomap...")
    im = Infomap((args if args else '') + default_args)
    network.apply(im)
    im.run()
    im.write_flow_tree(path.join(outdir, filename) + ".ftree", states=True)
    print(f"[infomap] codelength {im.codelength}")
    print(f"[infomap] num top modules {im.num_top_modules}")


def run(file,
        outdir="output",
        outfile=None,
        multilayer=False,
        multilayer_similarity=False,
        bipartite=False,
        bipartite_non_backtracking=False,
        unipartite_undirected=False,
        unipartite_directed=False,
        self_links=False,
        write_network=False,
        largest_cc=False,
        **kwargs) -> Optional[Network]:
    hypergraph = HyperGraph.from_iter(file.readlines())

    if largest_cc:
        hypergraph = largest_connected_component(hypergraph)

    hypergraph = remove_simple_hyperedges(hypergraph)

    if multilayer or multilayer_similarity:
        network = representation.multilayer(hypergraph, multilayer_similarity, self_links=self_links)

        basename = outfile if outfile else "multilayer"
        basename += "_similarity" if multilayer_similarity else ""
        basename += "_self_links" if self_links else ""

    elif bipartite or bipartite_non_backtracking:
        network = representation.bipartite(hypergraph, bipartite_non_backtracking)

        basename = outfile if outfile else "bipartite"
        basename += "_non_backtracking" if bipartite_non_backtracking else ""

    elif unipartite_undirected or unipartite_directed:
        network = representation.unipartite(hypergraph, unipartite_directed, self_links)

        basename = outfile if outfile else "unipartite"
        basename += "_directed" if unipartite_directed else "_undirected"
        basename += "_self_links" if self_links else ""

    else:
        return

    if write_network:
        network_filename = path.join(outdir, basename) + ".net"
        with open(network_filename, "w") as fp:
            network.write(fp)

    args = "--bipartite-teleportation" \
        if bipartite or bipartite_non_backtracking else None

    run_infomap(basename,
                outdir,
                network,
                args=args,
                directed=not unipartite_undirected,
                self_links=self_links,
                **kwargs)

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

    parser.add_argument("--largest-cc", action="store_true",
                        help="only include largest connected component")
    parser.add_argument("-w", "--write-network", action="store_true", help="write network representation to file")
    parser.add_argument("-k", "--self-links", action="store_true",
                        help="include self links (does not apply to bipartite representations)")
    parser.add_argument("-2", "--two-level", action="store_true",
                        help="only search for two-level partitions")
    parser.add_argument("--no-infomap", action="store_true", help="do not run Infomap")
    parser.add_argument("-s", "--seed", default=_DEFAULT_SEED, type=int, help="random seed")
    parser.add_argument("-p", "--teleportation-probability", default=_DEFAULT_TELEPORTATION_PROB,
                        type=float, help="probability to teleport in each step")
    parser.add_argument("-o", "--outfile")

    output = parser.add_argument_group("representation")
    options = output.add_mutually_exclusive_group(required=True)
    options.add_argument("-m", "--multilayer", action="store_true")
    options.add_argument("-M", "--multilayer-similarity", action="store_true")
    options.add_argument("-b", "--bipartite", action="store_true")
    options.add_argument("-B", "--bipartite-non-backtracking", action="store_true")
    options.add_argument("-u", "--unipartite-undirected", action="store_true")
    options.add_argument("-U", "--unipartite-directed", action="store_true")

    args = parser.parse_args()

    run(**vars(args))


if __name__ == "__main__":
    main()
