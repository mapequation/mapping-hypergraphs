from typing import Sequence, Tuple, List

from sklearn.metrics import adjusted_mutual_info_score

from similarity.tree import Level, TreeNode

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


def ami(*args, **kwargs) -> float:
    return adjusted_mutual_info_score(*labels_pair(*args, **kwargs))
