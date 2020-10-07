from typing import Tuple, Sequence

from references.parse_references import parse


def vertex(node_id: int, name: str) -> str:
    return "{} \"{}\"\n".format(node_id, name)


def hyperedge(edge_id: str, node_ids: Sequence[int], omega: int) -> str:
    ids = " ".join(map(str, node_ids))
    return "{} {} {}\n".format(edge_id, ids, omega)


def weight(edge_id: int, node_id: int, gamma: int) -> str:
    return "{} {} {}\n".format(edge_id, node_id, gamma)


def omega_unweighted(_: int) -> int:
    return 1


def omega_weighted(n: int) -> int:
    return n


def gamma_unweighted(n: int) -> Tuple[int, ...]:
    return (1,) * n


def gamma_weighted(n: int) -> Tuple[int, ...]:
    if n == 1:
        return 2,
    else:
        return (2,) + (1,) * (n - 2) + (2,)


def write_hypergraph(hypergraph,
                     outfile,
                     omega_function=omega_unweighted,
                     gamma_function=gamma_unweighted):
    unique_nodes = {node for nodes in hypergraph for node in nodes}
    nodes = {name: i + 1 for i, name in enumerate(unique_nodes)}

    outfile.write("*Vertices\n")
    outfile.writelines(vertex(node_id, name) for name, node_id in nodes.items())

    edges = {i + 1: tuple(nodes[name] for name in names)
             for i, names in enumerate(hypergraph)}

    outfile.write("*Hyperedges\n")
    outfile.writelines(hyperedge(edge_id, node_ids, omega_function(len(node_ids)))
                       for edge_id, node_ids in edges.items())

    outfile.write("*Weights\n")
    outfile.writelines(weight(edge_id, node_id, gamma)
                       for edge_id, node_ids in edges.items()
                       for node_id, gamma in zip(node_ids, gamma_function(len(node_ids))))


if __name__ == "__main__":
    with open("data/networks-beyond-pairwise-interactions-references.tex") as texfile, \
            open("data/networks-beyond-pairwise-interactions.txt", "w") as outfile:
        write_hypergraph(parse(texfile), outfile)
