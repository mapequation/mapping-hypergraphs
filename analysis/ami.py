from collections import defaultdict
from itertools import combinations_with_replacement, starmap
from typing import Sequence, List

import numpy as np
import pandas as pd
from sklearn.metrics import adjusted_mutual_info_score

from hypergraph.network import Level, TreeNode, Tree

Labels = List[int]


def module_level(nodes: Sequence[TreeNode], level: Level = Level.LEAF_MODULE) -> Labels:
    return [node.level(level)
            for node in sorted(nodes, key=lambda n: n.state_id)]


def ami(networks: Sequence[Tree], **kwargs) -> pd.DataFrame:
    ami_ = np.zeros(shape=(len(networks),) * 2)

    index = defaultdict(lambda: len(index))

    for network1, network2 in combinations_with_replacement(networks, 2):
        j = index[network1.pretty_filename]
        i = index[network2.pretty_filename]

        labels1, labels2 = starmap(module_level, ((network1.nodes, kwargs), (network2.nodes, kwargs)))

        if len(labels1) != len(labels2):
            raise RuntimeWarning("Different sets of labels")

        ami_[i, j] = adjusted_mutual_info_score(labels1, labels2)

    return pd.DataFrame(data=ami_, columns=list(index.keys()))
