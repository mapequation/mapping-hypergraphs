from hypergraph.main import main

if __name__ == "__main__":
    from argparse import ArgumentParser, FileType
    import sys

    parser = ArgumentParser()
    parser.add_argument("--self-links", const=True, default=False, action="store_const")
    parser.add_argument("--bipartite-non-backtracking", const=True, default=False, action="store_const")
    parser.add_argument("--shifted", const=True, default=False, action="store_const")
    parser.add_argument("filename", type=FileType("r"), default=sys.stdin)

    args = parser.parse_args()

    main(args.filename,
         backtracking=not args.bipartite_non_backtracking,
         self_links=args.self_links,
         shifted=args.shifted)
