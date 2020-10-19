import subprocess
from collections import defaultdict, namedtuple
from itertools import combinations_with_replacement, product
from typing import Sequence, Dict, Tuple, Any, Iterable

import numpy as np
import pandas as pd

from hypergraph.network import TreeNode, Tree


def assignment_id(path: Tuple[int]) -> Iterable[int]:
    assignment_id_ = defaultdict(lambda: len(assignment_id_))

    for i in range(1, len(path)):
        yield assignment_id_[path[0:i]]


Partition = namedtuple("Partition", "assignments, cluster_sizes")


def make_partition(nodes: Sequence[TreeNode]) -> Partition:
    assignments = {node.state_id: tuple(assignment_id(node.path))
                   for node in nodes}

    cluster_sizes = defaultdict(int)

    for node in assignments:
        for assignment in assignments[node]:
            cluster_sizes[assignment] += 1

    return Partition(assignments, dict(cluster_sizes))


def dict_iter_values(dict1: Dict[Any, Any], dict2: Dict[Any, Any]):
    for key in dict1:
        yield dict1[key], dict2[key]


def weighted_jaccard_distance(p1: Partition, p2: Partition) -> float:
    intersections = defaultdict(int)

    for assignments1, assignments2 in dict_iter_values(p1.assignments, p2.assignments):
        for assignment1, assignment2 in product(assignments1, assignments2):
            intersections[assignment1, assignment2] += 1

    intersections = dict(intersections)

    max_similarities_1 = defaultdict(float)
    max_similarities_2 = defaultdict(float)

    for (assignment1, assignment2), intersection in intersections.items():
        union = p1.cluster_sizes[assignment1] + p2.cluster_sizes[assignment2] - intersection
        if union == 0:
            continue

        similarity = intersection / union

        max_similarities_1[assignment1] = max(similarity, max_similarities_1[assignment1])
        max_similarities_2[assignment2] = max(similarity, max_similarities_2[assignment2])

    s1 = np.inner(*zip(*dict_iter_values(p1.cluster_sizes, max_similarities_1))) / sum(p1.cluster_sizes.values())
    s2 = np.inner(*zip(*dict_iter_values(p2.cluster_sizes, max_similarities_2))) / sum(p2.cluster_sizes.values())

    return 1 - 0.5 * s1 - 0.5 * s2


def wjaccard(filename1: str, filename2: str, cmd: str = "wjaccarddist") -> float:
    result = subprocess.run([cmd, filename1, filename2], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        result.check_returncode()
    except subprocess.CalledProcessError:
        raise Exception(result.stderr.decode("utf-8"))

    return float(result.stdout)


def weighted_jaccard_dist(networks: Sequence[Tree]) -> pd.DataFrame:
    dist = np.zeros(shape=(len(networks),) * 2)

    index = {network.pretty_filename: i
             for i, network in enumerate(networks)}

    partitions = {index[network.pretty_filename]: make_partition(network.nodes)
                  for network in networks}

    for network1, network2 in combinations_with_replacement(networks, 2):
        j = index[network1.pretty_filename]
        i = index[network2.pretty_filename]

        dist[i, j] = 1 - weighted_jaccard_distance(partitions[i], partitions[j])

    return pd.DataFrame(data=dist, columns=list(index.keys()))


if __name__ == "__main__":
    print(wjaccard("output/clique_seed_1.ftree", "output/clique_directed_seed_1.ftree"))
