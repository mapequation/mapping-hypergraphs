import os
import re
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from itertools import filterfalse, takewhile, dropwhile
from operator import attrgetter
from typing import Tuple, Optional, Iterable, List, Callable, Dict, Sequence, TextIO, Set, Mapping

from hypergraph.network import StateNetwork

Path = Tuple[int, ...]


class Level(Enum):
    TOP_MODULE = 0
    LEAF_MODULE = -2


@dataclass
class TreeNode:
    path: Path
    flow: float
    name: str
    id: int
    state_id: Optional[int] = None
    layer_id: Optional[int] = None

    def write(self, fp: TextIO):
        fp.write("{} {} \"{}\" {} {}\n".format(":".join(map(str, self.path)),
                                               self.flow,
                                               self.name,
                                               self.state_id if self.state_id is not None else self.id,
                                               self.id))

    @property
    def top_module(self) -> int:
        return self.path[0]

    @property
    def module(self) -> str:
        return ":".join(map(str, self.path[:-1]))

    def level(self, level: Level):
        if level == Level.TOP_MODULE:
            return self.top_module

        return self.module

    @classmethod
    def from_str(cls, line: str):
        line = line.strip()

        name, state_id, layer_id = None, None, None

        name_begin, name_end = line.index("\""), line.rindex("\"")

        if name_begin >= name_end:
            raise RuntimeError("Could not parse name from line \"{line}\"")

        name = line[name_begin + 1:name_end]

        line = line[:name_begin - 1] + line[name_end + 1:]

        path, flow, *ids = line.split()
        path, flow, ids = tuple(map(int, path.split(":"))), float(flow), tuple(map(int, ids))

        if len(ids) == 2:
            state_id, node_id = ids
        elif len(ids) == 3:
            state_id, node_id, layer_id = ids
        else:
            node_id = ids[0]

        return TreeNode(path, flow, name if name else str(node_id), node_id, state_id, layer_id)


def is_feature_node(line: str) -> bool:
    return "hyperedge" in line.lower()


def pretty_filename(filename: str) -> str:
    basename = os.path.basename(filename)
    name, _ = os.path.splitext(basename)
    name = re.sub(r"_seed_\d+$", "", name)

    representation, *kind = name.replace("_", " ").split()
    kind = " ".join(kind)

    if "backtracking" in kind:
        kind = "non-bt"

    return f"{representation} ({kind})" if kind else representation


@dataclass
class Tree:
    nodes: List[TreeNode]
    is_bipartite: bool = False
    is_multilayer: bool = False
    filename: Optional[str] = None

    @property
    def pretty_filename(self) -> str:
        if not self.filename:
            return str(self)

        return pretty_filename(self.filename)

    def write(self, fp: TextIO):
        for node in self.nodes:
            node.write(fp)

    @classmethod
    def from_file(cls, filename: str, **kwargs):  # -> Tree
        with open(filename) as fp:
            return cls.from_iter(fp.readlines(), filename=filename, **kwargs)

    @classmethod
    def from_files(cls, filenames: Sequence[str]):  # -> List[Tree]
        return [cls.from_file(name, is_multilayer="multilayer" in name, is_bipartite="bipartite" in name)
                for name in filenames]

    @classmethod
    def from_iter(cls,
                  iterable: Iterable[str],
                  node_filter: Optional[Callable[[str], bool]] = is_feature_node,
                  **kwargs):
        no_commented_lines = dropwhile(lambda line: line.startswith("#"), iterable)
        nodes = takewhile(lambda line: not line.startswith("*"), no_commented_lines)

        if node_filter:
            nodes = filterfalse(node_filter, nodes)

        return cls(list(map(TreeNode.from_str, nodes)), **kwargs)

    def initial_partition(self, network: StateNetwork) -> Dict[int, int]:
        tree_nodes = {node.id: node for node in self.nodes}

        return {state_id: tree_nodes[node_id].top_module
                for state_id, node_id in network.states
                if node_id in tree_nodes}

    def cluster_data(self, network: StateNetwork):  # -> Tree
        tree_nodes = {node.id: node for node in self.nodes}

        path = make_indexed_path()

        zero_flow = 0.0

        mapped_nodes = (TreeNode(path(tree_nodes[node_id]),
                                 zero_flow,
                                 tree_nodes[node_id].name,
                                 node_id,
                                 state_id)
                        for state_id, node_id in network.states
                        if node_id in tree_nodes)

        return Tree(sorted(mapped_nodes, key=attrgetter("path")))

    @property
    def state_ids(self) -> Mapping[int, Set[int]]:
        state_ids = defaultdict(set)  # node id -> set of state ids

        for node in self.nodes:
            state_ids[node.id].add(node.state_id)

        return dict(state_ids)

    @property
    def layer_ids(self) -> Mapping[Tuple[int, int], Set[int]]:
        layer_ids = defaultdict(int)  # (node id, layer id) -> state id

        for node in self.nodes:
            layer_ids[node.id, node.layer_id] = node.state_id

        return dict(layer_ids)

    def match_ids(self, networks) -> None:
        for network in networks:
            if network is self:
                continue

            if network.is_multilayer:
                self._match_multilayer_ids(network)
            else:
                self._match_network_ids(network)

    def _match_multilayer_ids(self, network) -> None:
        layer_ids = self.layer_ids

        for node in network.nodes:
            node.state_id = layer_ids[node.id, node.layer_id]

        network_state_ids = {node.state_id for node in network.nodes}

        missing_nodes = (node for node in self.nodes
                         if node.state_id not in network_state_ids)

        first_free_module_id = max(map(attrgetter("top_module"), network.nodes)) + 1

        network.nodes.extend(TreeNode((first_free_module_id + i, 1),
                                      0,
                                      missing_node.name,
                                      missing_node.id,
                                      missing_node.state_id)
                             for i, missing_node in enumerate(missing_nodes))

    def _match_network_ids(self, network) -> None:
        state_ids = self.state_ids

        missing_nodes = []

        # 0. we need to set the leaf node index correctly
        path = make_indexed_path(network.nodes)

        for node in network.nodes:
            # 1. set the state id of the already existing node
            # 2. add nodes for each remaining state node
            # 3. divide the flow evenly between them
            other_state_ids = state_ids[node.id].copy()

            node.flow /= len(other_state_ids)
            node.state_id = other_state_ids.pop()

            missing_nodes.extend(TreeNode(path(node),
                                          node.flow,
                                          node.name,
                                          node.id,
                                          other_state_id)
                                 for other_state_id in other_state_ids)

        network.nodes.extend(missing_nodes)
        network.nodes.sort(key=attrgetter("path"))


def make_indexed_path(nodes: Optional[Iterable[TreeNode]] = None) -> Callable[[TreeNode], Path]:
    leaf_index = defaultdict(int)

    def path(node: TreeNode) -> Path:
        module = node.path[:-1]
        leaf_index[module] += 1
        return *module, leaf_index[module]

    if nodes:
        for node in nodes:
            path(node)

    return path
