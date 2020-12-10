from os import path
from typing import Optional

from infomap import Infomap

from hypergraph import representation
from hypergraph.components import largest_connected_component
from hypergraph.network import HyperGraph, Network, remove_simple_hyperedges, Tree, StateNetwork

_DEFAULT_SEED = 123
_DEFAULT_TELEPORTATION_PROB = 0.15


def run_infomap(network: Network,
                basename: Optional[str] = None,
                outdir: Optional[str] = None,
                args: Optional[str] = None,
                directed: bool = True,
                self_links: bool = False,
                no_infomap: bool = False,
                two_level: bool = False,
                output_states: bool = True,
                seed: int = _DEFAULT_SEED,
                num_trials: int = 20,
                silent: bool = True,
                teleportation_probability: float = _DEFAULT_TELEPORTATION_PROB,
                **_) -> Infomap:
    default_args = f" --num-trials {num_trials if not no_infomap else 1}"
    default_args += " --silent" if silent else ""
    default_args += " --directed" if directed else ""
    default_args += " --include-self-links" if self_links else ""
    default_args += " --two-level" if two_level else ""
    default_args += " --no-infomap" if no_infomap else ""
    default_args += f" --seed {seed}"
    default_args += f" --teleportation-probability {teleportation_probability}"

    filename = None

    if basename is not None:
        filename = basename + (f"_seed_{seed}" if seed != _DEFAULT_SEED else "")
        default_args += f" --out-name {filename} "

    if outdir is not None:
        if output_states:
            default_args += " -o states "

        default_args += outdir

    print("[infomap] running infomap...")
    im = Infomap((args if args else '') + default_args)
    network.apply(im)
    im.run()

    if filename is not None:
        outname = path.join(outdir, filename) + ".ftree"
        im.write_flow_tree(outname, states=True)

        with open(outname, "r") as fp:
            original = fp.read()
        with open(outname, "w") as fp:
            fp.write(f"# codelengths {','.join(map(str, im.codelengths))}\n")
            fp.write(f"# num leaf modules {im.num_leaf_modules}\n")
            fp.write(original)

    print(f"[infomap] codelength {im.codelength}")
    print(f"[infomap] num top modules {im.num_top_modules}")

    return im


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
        pre_cluster_multilayer=False,
        **kwargs) -> Optional[Network]:
    hypergraph = HyperGraph.from_iter(file.readlines())

    if largest_cc:
        hypergraph = largest_connected_component(hypergraph)

    hypergraph = remove_simple_hyperedges(hypergraph)

    args = None

    if multilayer or multilayer_similarity:
        network = representation.multilayer(hypergraph, multilayer_similarity, self_links=self_links)

        basename = outfile if outfile else "multilayer"
        basename += "_similarity" if multilayer_similarity else ""
        basename += "_self_links" if self_links else ""

        if pre_cluster_multilayer:
            unipartite = representation.unipartite(hypergraph, directed=True, self_links=self_links)

            unipartite_basename = "multilayer_flattened"

            # Optimize the unipartite projection
            run_infomap(unipartite, unipartite_basename, path.join(outdir, "multilayer"), self_links=self_links,
                        output_states=False, **kwargs)

            unipartite_tree = Tree.from_file(path.join(path.join(outdir, "multilayer"), unipartite_basename + ".ftree"))

            # Run infomap without optimizing to get the tree and state network
            run_infomap(network, basename, outdir, self_links=self_links, output_states=True,
                        args="--no-infomap", num_trials=1, **kwargs)

            multilayer_tree = Tree.from_file(path.join(outdir, basename + ".ftree"))
            multilayer_tree.match_ids((unipartite_tree,))

            unipartite_tree.write()
            args = f"--cluster-data {unipartite_tree.filename} -F"

            network = StateNetwork.from_file(path.join(outdir, basename + "_states.net"))

    elif bipartite or bipartite_non_backtracking:
        args = "--bipartite-teleportation"

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

    run_infomap(network,
                basename,
                outdir,
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
    parser.add_argument("--num-trials", default=20, type=int, help="number of times to run Infomap")
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
