import os
import pickle
from collections import defaultdict
from statistics import mode, median, mean

from hypergraph import representation
from hypergraph.components import largest_connected_component
from hypergraph.main import run_infomap
from hypergraph.network import HyperGraph, remove_simple_hyperedges, Tree


def get_effective_assignments(hypergraph, self_links, similarity):
    pickle_filename = f"multilayer{'_self_links' if self_links else ''}{'_similarity' if similarity else ''}.pickle"

    if not os.path.isfile(pickle_filename):

        multilayer = representation.multilayer(hypergraph, similarity_walk=similarity, self_links=self_links)

        im = run_infomap(multilayer, directed=True, self_links=self_links)

        tree = Tree.from_infomap(im)

        effective_assignments = tree.effective_assignments

        with open(pickle_filename, "wb") as fp:
            pickle.dump(effective_assignments, fp)
    else:
        with open(pickle_filename, "rb") as fp:
            effective_assignments = pickle.load(fp)
    return effective_assignments


def main(file):
    hypergraph = HyperGraph.from_iter(file.readlines())
    hypergraph = largest_connected_component(hypergraph)
    hypergraph = remove_simple_hyperedges(hypergraph)

    print(f"Num nodes: {len(hypergraph.nodes)}")

    num_coauthors = [len(edge.nodes) for edge in hypergraph.edges]

    print(f"Median coauthors {median(num_coauthors)}")

    contributions = defaultdict(int)

    for _, node, _ in hypergraph.weights:
        contributions[node.id] += 1

    print(f"Mean contributions: {mean(contributions.values())}")
    print(f"Mode contributions: {mode(contributions.values())}")

    effective_assignments = defaultdict(list)

    for self_links in (True, False):
        for similarity in (False, True):
            for name, assignments in get_effective_assignments(hypergraph, self_links, similarity).items():
                effective_assignments[name].append(assignments)

    effective_assignments = {name: assignments for name, assignments in effective_assignments.items()
                             if any(map(lambda x: x > 1, assignments))}

    effective_assignments = dict(sorted(effective_assignments.items(), key=lambda x: mean(x[1]), reverse=True))

    for name, assignments in effective_assignments.items():
        print(f"{name:23}", assignments)


if __name__ == "__main__":
    with open("../data/references-weighted.txt") as fp:
        main(fp)
