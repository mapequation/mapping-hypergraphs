from collections import defaultdict
from itertools import combinations
from typing import Tuple, List, Iterable, Optional, Dict

import numpy as np
import pandas as pd
from sklearn.metrics import adjusted_mutual_info_score

from .helpers import pretty_filename
from .tree import TreeNode


def ami_score(nodes1: Iterable[TreeNode], nodes2: Iterable[TreeNode]) -> Optional[float]:
    labels1, ids1 = labels(nodes1)
    labels2, ids2 = labels(nodes2, ids1)

    if len(labels1) != len(labels2):
        return

    return adjusted_mutual_info_score(labels1, labels2)


def ami_matrix(nodes, filenames) -> Tuple[pd.DataFrame, List[str]]:
    ami = np.identity(len(filenames))

    index = defaultdict(lambda: len(index))

    for (nodes1, name1), (nodes2, name2) in combinations(zip(nodes, filenames), 2):
        j = index[pretty_filename(name1)]
        i = index[pretty_filename(name2)]
        ami[i][j] = ami_score(nodes1, nodes2)

    return pd.DataFrame(data=ami, columns=list(index.keys())), list(index.keys())


Labels = List[int]
Ids = Dict[str, int]


def labels(nodes: Iterable[TreeNode], ids: Optional[Ids] = None) -> Tuple[Labels, Ids]:
    if ids:
        ids_ = defaultdict(lambda: len(ids_), ids)
    else:
        ids_ = defaultdict(lambda: len(ids_))

    labels_ = {}

    for node in nodes:
        node_id = ids_[node.name]
        labels_[node_id] = node.top_module

    return [labels_[node_id] for node_id in sorted(labels_.keys())], dict(ids_)
