import glob
import os
from collections import defaultdict
from itertools import combinations_with_replacement, takewhile, dropwhile
from typing import Sequence, Iterable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from similarity.ami import ami
from similarity.tree import TreeNode, Level, Tree
from similarity.wjaccard import wjaccard


def plot_heatmap(data: pd.DataFrame, title: str, **kwargs) -> plt.Figure:
    plt.figure()

    plot = sns.heatmap(data,
                       mask=np.triu(np.ones_like(data, dtype=bool), k=1),
                       yticklabels=data.columns,
                       cmap=(sns.color_palette("viridis", as_cmap=True)),
                       annot=True,
                       annot_kws={"fontsize": 8},
                       fmt=".2g",
                       square=True,
                       linewidths=.5,
                       **kwargs)

    plt.title(title)
    plt.subplots_adjust(bottom=0.28)
    plt.show()

    return plot.get_figure()


def match_ids(ground_truth: Tree, trees: Iterable[Tree]):
    state_ids = defaultdict(set)  # node id -> set of state other_state_ids
    layer_ids = defaultdict(int)  # (node id, layer id) -> state id

    for node in ground_truth.nodes:
        state_ids[node.id].add(node.state_id)
        layer_ids[node.id, node.layer_id] = node.state_id

    state_ids = dict(state_ids)
    layer_ids = dict(layer_ids)

    for tree in trees:
        if tree.is_multilayer:
            multilayer_state_ids = set()

            for node in tree.nodes:
                node.state_id = layer_ids[node.id, node.layer_id]
                multilayer_state_ids.add(node.state_id)

            missing_nodes = (node for node in ground_truth.nodes
                             if node.state_id not in multilayer_state_ids)

            first_free_module_id = max(node.top_module for node in tree.nodes) + 1

            tree.nodes.extend(TreeNode((first_free_module_id + i, 1),
                                       0,
                                       missing_node.name,
                                       missing_node.id,
                                       missing_node.state_id)
                              for i, missing_node in enumerate(missing_nodes))

        else:
            missing_nodes = []

            for node in tree.nodes:
                # 1. set the state id of the already existing node
                # 2. add nodes for each remaining state node
                # 3. divide the flow evenly between them
                other_state_ids = state_ids[node.id].copy()

                node.flow /= len(other_state_ids)
                node.state_id = other_state_ids.pop()

                missing_nodes.extend(TreeNode(node.path,
                                              node.flow,
                                              node.name,
                                              node.id,
                                              other_state_id)
                                     for other_state_id in other_state_ids)

            tree.nodes.extend(missing_nodes)


def summarize(networks: Sequence[Tree]):
    summary = []

    for network in networks:
        name = network.filename

        with open(name) as fp:
            lines = fp.readlines()
            header = takewhile(lambda line: line.startswith("#"), lines)
            # partitioned into 4 levels with 286 top modules
            levels = int(next(filter(lambda line: line.startswith("# partitioned into"), header)).split()[3])
            # codelength 3.11764 bits
            codelength = float(next(filter(lambda line: line.startswith("# codelength"), header)).split()[2])

            states_filename = os.path.splitext(name)[0] + "_states.net"

            with open(states_filename) as states_fp:
                states_lines = states_fp.readlines()

                num_states = len(list(takewhile(lambda line: not line.startswith("*Links"),
                                                dropwhile(lambda line: not line.startswith("# stateId physicalId"),
                                                          states_lines))))

                num_links = len(list(dropwhile(lambda line: not line.startswith("*Links"), states_lines)))

                summary.append((network.pretty_filename, num_states, num_links, levels, codelength))

    for line in summary:
        print("{:26} & {} & {:5} & {} & {:.3f} \\\\".format(*line))


def main(filenames: Sequence[str]):
    networks = [Tree.from_file(name, is_multilayer="multilayer" in name, is_bipartite="bipartite" in name)
                for name in filenames]

    summarize(networks)

    multilayer = next((network for network in networks if "multilayer_self_links" in network.filename), None)

    if multilayer:
        match_ids(multilayer, (network for network in networks if network != multilayer))

    outdir = "output/matched_ids"
    existing_files = glob.glob(outdir + "/*")
    for f in existing_files:
        os.remove(f)

    for network in networks:
        with open(os.path.join(outdir, os.path.basename(network.filename)), "w") as fp:
            for node in network.nodes:
                node.write(fp)

    ami_top = np.zeros(shape=(len(networks),) * 2)
    ami_leaf = np.zeros_like(ami_top)
    jaccard = np.zeros_like(ami_top)

    index = defaultdict(lambda: len(index))

    for network1, network2 in combinations_with_replacement(networks, 2):
        j = index[network1.pretty_filename]
        i = index[network2.pretty_filename]

        ami_top[i, j] = ami(network1.nodes, network2.nodes, level=Level.TOP_MODULE)

        ami_leaf[i, j] = ami(network1.nodes, network2.nodes, level=Level.LEAF_MODULE)

        jaccard[i, j] = 1 - wjaccard(os.path.join("output/matched_ids", os.path.basename(network1.filename)),
                                     os.path.join("output/matched_ids", os.path.basename(network2.filename)))

    ticklabels = list(index.keys())
    plot_heatmap(pd.DataFrame(data=ami_top, columns=ticklabels), title="AMI (Top modules)")
    plot_heatmap(pd.DataFrame(data=ami_leaf, columns=ticklabels), title="AMI (Leaf modules)")
    plot_heatmap(pd.DataFrame(data=jaccard, columns=ticklabels), title="1 - Weighted Jaccard distance")


if __name__ == "__main__":
    names = (os.path.join("output", name) for name in sorted(os.listdir("output")))
    filenames = [name for name in names if os.path.isfile(name) and name.endswith("tree")]

    main(filenames)
