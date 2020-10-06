import os
from typing import Sequence, Iterable

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from similarity.ami import ami_matrix
from similarity.tree import TreeNode, tree_nodes


def read_files(filenames: Sequence[str]) -> Iterable[Iterable[TreeNode]]:
    for filename in filenames:
        with open(filename) as fp:
            yield tree_nodes(fp.readlines())


def plot_heatmap(similarity, labels, filename=None):
    mask = np.triu(np.ones_like(similarity, dtype=bool))

    cmap = sns.color_palette("rocket_r", as_cmap=True)

    plt.figure()
    plot = sns.heatmap(similarity, mask=mask, yticklabels=labels, cmap=cmap,
                       square=True, linewidths=.5, cbar_kws={"shrink": .5})

    plt.subplots_adjust(bottom=0.28)
    plt.show()

    if filename:
        plot.get_figure().savefig(filename)


def main(filenames: Sequence[str]):
    nodes = read_files(filenames)
    ami, labels = ami_matrix(nodes, filenames)
    plot_heatmap(ami, labels)


if __name__ == "__main__":
    names = (os.path.join("output", name) for name in sorted(os.listdir("output")))
    filenames = [name for name in names if os.path.isfile(name) and name.endswith("tree")]
    filenames = [name for name in filenames if not "multilayer" in name]

    main(filenames)
