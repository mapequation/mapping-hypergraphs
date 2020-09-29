from hypergraph.io import read_lines
from hypergraph.parse import parse


def main(filename):
    with open(filename, "r") as fp:
        data = read_lines(fp.read())

    nodes, hyperedges, weights = parse(data)
    print(nodes)
    print(hyperedges)
    print(weights)


if __name__ == "__main__":
    main("data.txt")
