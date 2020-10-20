import math
from typing import Tuple, Sequence, Union

from references.get_citations import get_citations
from references.parse_references import parse

Weight = Union[int, float]


def vertex(node_id: int, name: str) -> str:
    return "{} \"{}\"\n".format(node_id, name)


def hyperedge(edge_id: str, node_ids: Sequence[int], omega: Weight) -> str:
    ids = " ".join(map(str, node_ids))
    return "{} {} {}\n".format(edge_id, ids, omega)


def weight(edge_id: int, node_id: int, gamma: Weight) -> str:
    return "{} {} {}\n".format(edge_id, node_id, gamma)


def omega_unweighted(*_) -> Weight:
    return 1


def omega_weighted(node_ids: Tuple[int, ...], *_) -> Weight:
    return len(node_ids)


def omega_citations(_, *args) -> Weight:
    return get_citations(*args) + 1


def omega_log_citations(_, *args) -> Weight:
    return math.log(get_citations(*args) + 1) + 1


def gamma_unweighted(n: int, **_) -> Tuple[Weight, ...]:
    return (1,) * n


def gamma_weighted(n: int, equal_contributions=False) -> Tuple[Weight, ...]:
    if n > 1 and equal_contributions:
        return (1,) * n
    elif n == 1:
        return 2,
    else:
        return (2,) + (1,) * (n - 2) + (2,)


def is_sorted(authors: Sequence[str]):
    return sorted(authors) == authors


def write_hypergraph(hypergraph,
                     outfile,
                     omega_function=omega_unweighted,
                     gamma_function=gamma_unweighted):
    unique_nodes = {node for nodes in hypergraph for node in nodes.authors}
    nodes = {name: i + 1 for i, name in enumerate(sorted(unique_nodes))}
    last_names = {i: name.split()[-1] for name, i in nodes.items()}

    outfile.write("*Vertices\n")
    outfile.writelines(vertex(node_id, name) for name, node_id in nodes.items())

    edges = {i + 1: tuple(nodes[name] for name in node.authors)
             for i, node in enumerate(hypergraph)}

    articles = {i + 1: (node.title, node.authors[0])
                for i, node in enumerate(hypergraph)}

    outfile.write("*Hyperedges\n")
    outfile.writelines(hyperedge(edge_id, edge, omega_function(edge, *articles[edge_id], edge_id))
                       for edge_id, edge in edges.items())

    outfile.write("*Weights\n")
    outfile.writelines(weight(edge_id, node_id, gamma)
                       for edge_id, node_ids in edges.items()
                       for node_id, gamma in zip(node_ids,
                                                 gamma_function(len(node_ids),
                                                                equal_contributions=is_sorted(
                                                                    [last_names[node_id] for node_id in node_ids]))))


if __name__ == "__main__":
    with open("data/networks-beyond-pairwise-interactions-references.tex") as texfile, \
            open("data/networks-beyond-pairwise-interactions.txt", "w") as outfile:
        write_hypergraph(parse(texfile), outfile, omega_function=omega_citations)
