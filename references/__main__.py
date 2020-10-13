from argparse import ArgumentParser, FileType

from references.parse_references import parse
from references.write_hypergraph import write_hypergraph, \
    gamma_unweighted, gamma_weighted, \
    omega_unweighted, omega_weighted, omega_citations

if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("infile", type=FileType("r"))
    parser.add_argument("outfile", type=FileType("w"))
    parser.add_argument("--gamma-weighted", dest="gamma_function",
                        default=gamma_unweighted, const=gamma_weighted, action="store_const")
    parser.add_argument("--omega", choices=("unweighted", "weighted", "citations"),
                        default="weighted")
    parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args()

    omega_functions = {
        "unweighted": omega_unweighted,
        "weighted": omega_weighted,
        "citations": omega_citations
    }

    write_hypergraph(parse(args.infile, args.verbose),
                     args.outfile,
                     gamma_function=args.gamma_function,
                     omega_function=omega_functions[args.omega])
