from hypergraph.main import main

if __name__ == "__main__":
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

    parser.add_argument("filename", type=FileType("r"), default=sys.stdin, help="the hypergraph file")
    parser.add_argument("outdir", nargs="?", default="output", help="directory to write output to")

    parser.add_argument("-n", "--network", action="store_true", help="write network representation to file")
    parser.add_argument("--no-infomap", action="store_true", help="do not run infomap")
    parser.add_argument("-s", "--shifted", default=False, action="store_true",
                        help="use shifted transition probability")

    output = parser.add_argument_group("representation")
    options = output.add_mutually_exclusive_group(required=True)
    options.add_argument("-m", "--multilayer", action="store_true")
    options.add_argument("-M", "--multilayer-self-links", action="store_true")
    options.add_argument("-b", "--bipartite", action="store_true")
    options.add_argument("-B", "--bipartite-non-backtracking", action="store_true")

    args = parser.parse_args()

    main(args.filename,
         outdir=args.outdir,
         network=args.network,
         no_infomap=args.no_infomap,
         shifted=args.shifted,
         multilayer=args.multilayer,
         multilayer_self_links=args.multilayer_self_links,
         bipartite=args.bipartite,
         bipartite_non_backtracking=args.bipartite_non_backtracking)
