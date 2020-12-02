from itertools import product
from multiprocessing import Pool

import numpy as np

from hypergraph import representation
from hypergraph.main import run_infomap
from hypergraph.network import HyperGraph, Node, HyperEdge, Gamma


def run_task(hypergraph,
             kind,
             self_links: bool = False,
             similarity_walk: bool = False,
             non_backtracking: bool = False):
    if kind == "unipartite":
        network = representation.unipartite(hypergraph, directed=True, self_links=self_links)
    elif kind == "bipartite":
        network = representation.bipartite(hypergraph, non_backtracking=non_backtracking)
    elif kind == "multilayer":
        network = representation.multilayer(hypergraph, similarity_walk=similarity_walk, self_links=self_links)
    else:
        raise RuntimeError(f"No such {kind = }")

    args = "--bipartite-teleportation" if kind == "bipartite" else None

    im = run_infomap(network, args=args, self_links=self_links, two_level=True)

    return im.codelength, im.num_top_modules


def main():
    nodes = [
        Node(1, "a"),
        Node(2, "b"),
        Node(3, "c"),
        Node(4, "d"),
        Node(5, "e"),
        Node(6, "f"),
        Node(7, "i"),
        Node(8, "h"),
        Node(9, "g"),
        Node(10, "j")
    ]

    weights = [
        Gamma(1, nodes[1 - 1], 2),
        Gamma(1, nodes[2 - 1], 1),
        Gamma(1, nodes[3 - 1], 2),

        Gamma(2, nodes[4 - 1], 2),
        Gamma(2, nodes[5 - 1], 1),
        Gamma(2, nodes[6 - 1], 2),

        Gamma(3, nodes[3 - 1], 2),
        Gamma(3, nodes[6 - 1], 2),
        Gamma(3, nodes[9 - 1], 1),

        Gamma(4, nodes[7 - 1], 2),
        Gamma(4, nodes[8 - 1], 1),
        Gamma(4, nodes[9 - 1], 2),

        Gamma(5, nodes[7 - 1], 2),
        Gamma(5, nodes[8 - 1], 1),
        Gamma(5, nodes[9 - 1], 1),
        Gamma(5, nodes[10 - 1], 2)
    ]

    hyperedges = {
        # top
        1: [1, 2, 3],
        # left
        2: [4, 5, 6],
        # middle
        3: [3, 6, 9],
        # right
        4: [7, 8, 9],
        # right overlapping
        5: [7, 8, 9, 10]
    }

    # edges to optimize
    edge_ids = [1, 2, 4]

    nodes_by_edge = {edge: frozenset(nodes[i - 1] for i in node_ids)
                     for edge, node_ids in hyperedges.items()}

    hypergraph = HyperGraph(nodes, [], weights)

    num_trials = 0

    index = {name: i for i, name in enumerate([
        "bipartite", "bipartite non bt",
        "unipartite", "unipartite self links",
        "multilayer", "multilayer self links",
        "multilayer similarity", "multilayer similarity self links"
    ])}

    solutions = []

    num_non_trivial_solutions = 0
    multilayer_similarity_oks = 0
    num_multilayer_better = 0
    num_multilayer_self_links_better = 0

    with Pool(processes=8) as pool:
        for omegas in product(np.linspace(1, 3, 3), repeat=len(edge_ids)):
            omega = dict(zip(edge_ids, omegas))

            # known fix-points
            omega[3] = 2.0
            omega[5] = 3.0

            hypergraph.edges = [HyperEdge(edge, nodes_by_edge[edge], omega[edge])
                                for edge in hyperedges]

            tasks = (
                (hypergraph, "bipartite", None, None, False),
                (hypergraph, "bipartite", None, None, True),
                (hypergraph, "unipartite", False),
                (hypergraph, "unipartite", True),
                (hypergraph, "multilayer", False),
                (hypergraph, "multilayer", True),
                (hypergraph, "multilayer", False, True),
                (hypergraph, "multilayer", True, True),
            )

            results = pool.starmap(run_task, tasks)

            num_trials += 1

            codelengths, num_top_modules = zip(*results)

            all_non_trivial_solutions = all(map(lambda x: x > 1, num_top_modules))

            if not all_non_trivial_solutions:
                continue

            num_non_trivial_solutions += 1

            multilayer_similarity_ok = num_top_modules[index["multilayer similarity"]] > 3 and \
                                       num_top_modules[index["multilayer similarity self links"]] > 3

            if not multilayer_similarity_ok:
                continue

            multilayer_similarity_oks += 1

            codelength_better = abs(codelengths[index["multilayer"]] - codelengths[index["unipartite"]]) > 1e-7
            self_links_codelength_better = abs(codelengths[index["multilayer self links"]] - codelengths[index["unipartite self links"]]) > 1e-7

            same_num_top_modules = num_top_modules[index["multilayer"]] == num_top_modules[index["unipartite"]]
            same_num_top_modules_self_links = num_top_modules[index["multilayer self links"]] == num_top_modules[index["unipartite self links"]]

            multilayer_better = codelength_better and same_num_top_modules
            multilayer_self_links_better = self_links_codelength_better and same_num_top_modules_self_links

            num_multilayer_better += 1 if multilayer_better else 0
            num_multilayer_self_links_better += 1 if multilayer_self_links_better else 0

            if multilayer_better or multilayer_self_links_better:
                solutions.append(omega)

    for solution in solutions:
        print(solution)

    print(f"{len(solutions)}/{num_trials} = {len(solutions) / num_trials:.3f}%")
    print(f"{num_non_trivial_solutions = }")
    print(f"{multilayer_similarity_oks = }")
    print(f"{num_multilayer_better = }")
    print(f"{num_multilayer_self_links_better = }")


if __name__ == "__main__":
    main()
