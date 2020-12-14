import math
import os
import re
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from itertools import filterfalse, takewhile, dropwhile
from operator import attrgetter
from typing import Tuple, Optional, Iterable, List, Callable, Dict, Sequence, TextIO, Mapping

from infomap import Infomap
from scipy.stats import entropy

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
        fp.write("{} {} \"{}\"".format(":".join(map(str, self.path)), self.flow, self.name))
        if self.state_id is not None:
            fp.write(f" {self.state_id}")
        fp.write(f" {self.id}")
        if self.layer_id is not None:
            fp.write(f" {self.layer_id}")
        fp.write("\n")

    @property
    def top_module(self) -> int:
        return self.path[0]

    @property
    def leaf_module(self) -> str:
        return ":".join(map(str, self.path[:-1]))

    def level(self, level: Level):
        # https://bugs.python.org/issue30545
        if level.value == Level.TOP_MODULE.value:
            return self.top_module
        elif level.value == Level.LEAF_MODULE.value:
            return self.leaf_module
        else:
            raise NotImplementedError(f"Must be either top or leaf module, not {level=}.")

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
    header: Optional[str]
    nodes: List[TreeNode]
    is_bipartite: bool = False
    is_multilayer: bool = False
    filename: Optional[str] = None
    levels: Optional[int] = None
    num_top_modules: Optional[int] = None
    num_leaf_modules: Optional[int] = None
    codelength: Optional[float] = None
    codelengths: Optional[Tuple[float]] = None
    completed_in: Optional[float] = None

    @property
    def pretty_filename(self) -> str:
        if not self.filename:
            return str(self)

        return pretty_filename(self.filename)

    def write(self, fp: Optional[TextIO] = None):
        did_open = fp is None

        if did_open:
            fp = open(self.filename, "w")

        if self.header is not None:
            fp.write(self.header)

        for node in self.nodes:
            node.write(fp)

        if did_open:
            fp.close()

    @classmethod
    def parse_header(cls, lines: Iterable[str]) \
            -> Tuple[float,
                     Optional[Tuple[float]],
                     float,
                     int,
                     int,
                     Optional[int],
                     Optional[str]]:
        try:
            header = list(takewhile(lambda line: line.startswith("#"), lines))
        except StopIteration:
            pass

        if len(header) == 0:
            return 0.0, None, 0.0, 0, 0, None, None

        line = next(filter(lambda line: line.startswith("# codelengths"), header), "").split()
        codelengths = tuple(map(float, line[2].split(",")))

        line = next(filter(lambda line: line.startswith("# num leaf modules"), header), "").split()
        num_leaf_modules = int(line[4])

        # completed in 2.49655 s
        line = next(filter(lambda line: line.startswith("# completed in"), header), "").split()
        completed_in = float(line[3])

        # partitioned into 4 levels with 286 top modules
        line = next(filter(lambda line: line.startswith("# partitioned into"), header), "").split()
        levels, num_top_modules = int(line[3]), int(line[6])

        # codelength 3.11764 bits
        line = next(filter(lambda line: line.startswith("# codelength "), header), "").split()
        codelength = float(line[2])

        return codelength, codelengths, completed_in, levels, num_top_modules, num_leaf_modules, "".join(header)

    @classmethod
    def from_file(cls, filename: str, **kwargs):  # -> Tree
        with open(filename) as fp:
            lines = fp.readlines()

            codelength, codelenghts, completed_in, levels, num_top_modules, num_leaf_modules, header = \
                cls.parse_header(lines)

            return cls.from_iter(lines,
                                 header,
                                 filename=filename,
                                 levels=levels,
                                 num_top_modules=num_top_modules,
                                 num_leaf_modules=num_leaf_modules,
                                 codelength=codelength,
                                 codelengths=codelenghts,
                                 completed_in=completed_in,
                                 **kwargs)

    @classmethod
    def from_files(cls, filenames: Sequence[str]):  # -> List[Tree]
        return [cls.from_file(name, is_multilayer="multilayer" in name, is_bipartite="bipartite" in name)
                for name in filenames]

    @classmethod
    def from_iter(cls,
                  iterable: Iterable[str],
                  header: Optional[str],
                  node_filter: Optional[Callable[[str], bool]] = is_feature_node,
                  **kwargs):
        no_commented_lines = dropwhile(lambda line: line.startswith("#"), iterable)
        nodes = takewhile(lambda line: not line.startswith("*"), no_commented_lines)

        if node_filter:
            nodes = filterfalse(node_filter, nodes)

        return cls(header, list(map(TreeNode.from_str, nodes)), **kwargs)

    @classmethod
    def from_infomap(cls, im: Infomap, states=True, **kwargs):  # -> Tree:
        tmp_filename = "/tmp/1nf0m4p.tree"

        im.write_tree(tmp_filename, states)

        self = cls.from_file(tmp_filename, **kwargs)

        os.remove(tmp_filename)

        return self

    @property
    def assignments(self) -> Mapping[str, int]:
        assignments_ = defaultdict(set)

        for node in self.nodes:
            assignments_[node.name].add(node.leaf_module)

        return {name: len(assignments)
                for name, assignments in assignments_.items()}

    @property
    def effective_assignments(self) -> Mapping[str, float]:
        assignments_ = defaultdict(lambda: defaultdict(int))

        for node in self.nodes:
            assignments_[node.name][node.leaf_module] += 1

        return {name: 2 ** entropy(list(node_assignments.values()), base=2)
                for name, node_assignments in assignments_.items()}

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

    def physical_nodes(self, level=1):
        phys_nodes: Dict[str, Dict[int, TreeNode]] = defaultdict(dict)

        for node in self.nodes:
            module = ":".join(map(str, node.path[0:level]))
            if node.id not in phys_nodes[module]:
                phys_nodes[module][node.id] = TreeNode(node.path[0:level], node.flow, node.name, node.id)

            else:
                phys_node = phys_nodes[module][node.id]
                phys_node.flow += node.flow

        return dict(phys_nodes)

    def match_ids(self, networks) -> None:
        for network in networks:
            if network is self:
                continue

            if network.is_multilayer:
                self._match_multilayer_ids(network)
            else:
                self._match_network_ids(network)

    def _match_multilayer_ids(self, network) -> None:
        state_ids = {(node.id, node.layer_id): node.state_id for node in self.nodes}

        for node in network.nodes:
            node.state_id = state_ids[node.id, node.layer_id]

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
        self_state_nodes = defaultdict(list)

        for node in self.nodes:
            self_state_nodes[node.id].append(node)

        self_state_nodes = dict(self_state_nodes)

        missing_nodes = []

        # 0. we need to set the leaf node index correctly
        path = make_indexed_path(network.nodes)

        for node in network.nodes:
            # 1. set the state id of the already existing node
            # 2. add nodes for each remaining state node
            # 3. divide the flow between them
            state_nodes = self_state_nodes[node.id]

            first, *remaining = state_nodes
            node.state_id = first.state_id

            divide_flow = not math.isclose(node.flow, sum(node.flow for node in state_nodes), rel_tol=0.01)

            if divide_flow:
                node.flow /= len(state_nodes)
            else:
                node.flow = first.flow

            missing_nodes.extend(TreeNode(path(node),
                                          node.flow if divide_flow else state_node.flow,
                                          node.name,
                                          node.id,
                                          state_node.state_id)
                                 for state_node in remaining)

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
