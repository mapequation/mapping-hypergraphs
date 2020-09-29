from hypergraph import main

if __name__ == "__main__":
    from argparse import ArgumentParser, FileType
    import sys

    parser = ArgumentParser()
    parser.add_argument("--shifted", const=True, default=False, action="store_const")
    parser.add_argument("filename", type=FileType("r"), default=sys.stdin)

    args = parser.parse_args()

    main(args.filename, args.shifted)
