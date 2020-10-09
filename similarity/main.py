import os
from collections import defaultdict
from itertools import combinations_with_replacement
from typing import Sequence, Optional, Tuple, List, Mapping

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import adjusted_mutual_info_score

from similarity.tree import TreeNode, Level, Tree

Labels = List[int]
Ids = Mapping[str, int]


def labels(nodes: Sequence[TreeNode], ids: Optional[Ids] = None, level: Level = Level.TOP_MODULE, **kwargs) \
        -> Tuple[Labels, Ids]:
    if ids:
        ids_ = defaultdict(lambda: len(ids_), ids)
    else:
        ids_ = defaultdict(lambda: len(ids_))

    labels_ = {}

    for node in nodes:
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


def main(filenames: Sequence[str]):
    networks = [Tree.from_file(name) for name in filenames]

    level = Level.LEAF_MODULE

    ami = np.zeros(shape=(len(networks),) * 2)

    index = defaultdict(lambda: len(index))

    for network1, network2 in combinations_with_replacement(networks, 2):
        j = index[network1.pretty_filename]
        i = index[network2.pretty_filename]
        labels1, ids1 = labels(network1.nodes, level=level)
        labels2, ids2 = labels(network2.nodes, ids1, level=level)

        if len(labels1) != len(labels2):
            continue

        ami[i][j] = adjusted_mutual_info_score(labels1, labels2)

    ticklabels = list(index.keys())
    plot_heatmap(pd.DataFrame(data=ami, columns=ticklabels))


if __name__ == "__main__":
    names = (os.path.join("output", name) for name in sorted(os.listdir("output")))
    filenames = [name for name in names if os.path.isfile(name) and name.endswith("tree")]

    main(filenames)
