from collections import defaultdict
from itertools import combinations_with_replacement
from typing import Sequence, Tuple, List

import numpy as np
import pandas as pd
from sklearn.metrics import adjusted_mutual_info_score

from analysis.tree import Level, TreeNode, Tree

Labels = List[int]


def labels_pair(nodes1: Sequence[TreeNode], nodes2: Sequence[TreeNode], **kwargs) -> Tuple[Labels, Labels]:
    labels1, labels2 = labels(nodes1, **kwargs), labels(nodes2, **kwargs)

    if len(labels1) != len(labels2):
        raise RuntimeWarning("Different sets of labels")

    return labels1, labels2


def labels(nodes: Sequence[TreeNode], level: Level = Level.TOP_MODULE) -> Labels:
    labels_ = {}

    for node in nodes:
        if level == Level.TOP_MODULE:
            labels_[node.state_id] = node.top_module
        else:
            labels_[node.state_id] = node.module

    return [labels_[node_id] for node_id in sorted(labels_.keys())]


def ami(networks: Sequence[Tree], **kwargs) -> pd.DataFrame:
    ami_ = np.zeros(shape=(len(networks),) * 2)

    index = defaultdict(lambda: len(index))

    for network1, network2 in combinations_with_replacement(networks, 2):
        j = index[network1.pretty_filename]
        i = index[network2.pretty_filename]

        ami_[i, j] = adjusted_mutual_info_score(*labels_pair(network1.nodes, network2.nodes, **kwargs))

    return pd.DataFrame(data=ami_, columns=list(index.keys()))
