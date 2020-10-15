import glob
import os
from collections import defaultdict
from typing import Sequence, List, Iterable

from similarity.tree import Tree, TreeNode


def read_filenames(filenames: Sequence[str]) -> List[Tree]:
    return [Tree.from_file(name, is_multilayer="multilayer" in name, is_bipartite="bipartite" in name)
            for name in filenames]


def write_networks(networks: Sequence[Tree], outdir: str):
    for network in networks:
        with open(os.path.join(outdir, os.path.basename(network.filename)), "w") as fp:
            for node in network.nodes:
                node.write(fp)


def remove_files(directory: str):
    for f in glob.glob(directory + "/*"):
        os.remove(f)


def list_files(directory: str = "output") -> List[str]:
    names = (os.path.join(directory, name) for name in sorted(os.listdir(directory)))
    return [name for name in names if os.path.isfile(name) and name.endswith("tree")]


def match_ids(ground_truth_filename: str, networks: Iterable[Tree]):
    ground_truth = next((network for network in networks if ground_truth_filename in network.filename))

    networks_ = [network for network in networks if network != ground_truth]

    state_ids = defaultdict(set)  # node id -> set of state other_state_ids
    layer_ids = defaultdict(int)  # (node id, layer id) -> state id

    for node in ground_truth.nodes:
        state_ids[node.id].add(node.state_id)
        layer_ids[node.id, node.layer_id] = node.state_id

    state_ids = dict(state_ids)
    layer_ids = dict(layer_ids)

    for network in networks_:
        if network.is_multilayer:
            multilayer_state_ids = set()

            for node in network.nodes:
                node.state_id = layer_ids[node.id, node.layer_id]
                multilayer_state_ids.add(node.state_id)

            missing_nodes = (node for node in ground_truth.nodes
                             if node.state_id not in multilayer_state_ids)

            first_free_module_id = max(node.top_module for node in network.nodes) + 1

            network.nodes.extend(TreeNode((first_free_module_id + i, 1),
                                          0,
                                          missing_node.name,
                                          missing_node.id,
                                          missing_node.state_id)
                                 for i, missing_node in enumerate(missing_nodes))

        else:
            missing_nodes = []

            for node in network.nodes:
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

            network.nodes.extend(missing_nodes)
