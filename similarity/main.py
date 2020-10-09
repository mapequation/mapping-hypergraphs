import os
from collections import defaultdict
from itertools import combinations
from typing import Sequence, Optional, Tuple, List, Mapping

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import adjusted_mutual_info_score

from similarity.helpers import pretty_filename
from similarity.tree import TreeNode, tree_nodes, Level

Labels = List[int]
Ids = Mapping[str, int]


def labels(network: Sequence[TreeNode], ids: Optional[Ids] = None, level: Level = Level.TOP_MODULE, **kwargs) \
        -> Tuple[Labels, Ids]:
    if ids:
        ids_ = defaultdict(lambda: len(ids_), ids)
    else:
        ids_ = defaultdict(lambda: len(ids_))

    labels_ = {}

    for node in network:
        node_id = ids_[node.name]

        if level == Level.TOP_MODULE:
            labels_[node_id] = node.top_module
        else:
            labels_[node_id] = node.module

    labels_ = [labels_[node_id] for node_id in sorted(labels_.keys())]

    return labels_, dict(ids_)


def plot_heatmap(data: pd.DataFrame, **kwargs) -> plt.Figure:
    plt.figure()

    plot = sns.heatmap(data,
                       mask=np.triu(np.ones_like(data, dtype=bool), k=1),
                       yticklabels=data.columns,
                       cmap=(sns.color_palette("viridis", as_cmap=True)),
                       annot=True,
                       square=True,
                       linewidths=.5,
                       **kwargs)

    plt.subplots_adjust(bottom=0.28)
    plt.show()

    return plot.get_figure()


def read_files(filenames: Sequence[str]):
    for filename in filenames:
        with open(filename) as fp:
            yield tree_nodes(fp.readlines(), filename.startswith("bipartite"))


def main(filenames: Sequence[str]):
    networks = read_files(filenames)

    level = Level.LEAF_MODULE

    ami = np.zeros(shape=(len(filenames),) * 2)

    index = defaultdict(lambda: len(index))

    for (network1, name1), (network2, name2) in combinations(zip(networks, filenames), 2):
        j = index[pretty_filename(name1)]
        i = index[pretty_filename(name2)]
        labels1, ids1 = labels(network1, level=level)
        labels2, ids2 = labels(network2, ids1, level=level)

        if len(labels1) != len(labels2):
            continue

        ami[i][j] = adjusted_mutual_info_score(labels1, labels2)

    ticklabels = list(index.keys())
    plot_heatmap(pd.DataFrame(data=ami, columns=ticklabels))


if __name__ == "__main__":
    names = (os.path.join("output", name) for name in sorted(os.listdir("output")))
    filenames = [name for name in names if os.path.isfile(name) and name.endswith("tree")]

    main(filenames)
