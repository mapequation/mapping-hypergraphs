import os
import re
from dataclasses import dataclass
from enum import Enum
from itertools import filterfalse, takewhile, dropwhile
from typing import Tuple, Optional, Iterable, List, Callable

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

    def write(self, fp):
        fp.write("{} {} \"{}\" {} {}\n".format(":".join(map(str, self.path)),
                                               self.flow,
                                               self.name.title(),
                                               self.state_id if self.state_id else self.id,
                                               self.id))

    @property
    def rank(self) -> int:
        return self.path[-1]

    @property
    def top_module(self) -> int:
        return self.path[0]

    @property
    def leaf_module(self) -> int:
        return self.path[-2]

    @property
    def module(self) -> str:
        return ":".join(map(str, self.path[:-1]))

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

        basename = os.path.basename(self.filename)
        name, _ = os.path.splitext(basename)
        name = re.sub(r"_seed_\d+$", "", name)

        representation, *kind = name.replace("_", " ").split()
        kind = " ".join(kind)

        if "backtracking" in kind:
            kind = "non-bt"

        if "directed" in kind:
            kind = kind.replace("directed", "dir.")

        return "{} ({})".format(representation, kind) if kind else representation

    @classmethod
    def from_file(cls, filename: str, **kwargs):
        with open(filename) as fp:
            return Tree.from_iter(fp.readlines(), filename=filename, **kwargs)

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


if __name__ == "__main__":
    node = TreeNode.from_str("1:1:2 0.333333 \"c aoeu\" 1")
    print(node.module)
    print(TreeNode.from_str("1:1 0.333333 \"c aoeu\" 2 1"))
    print(TreeNode.from_str("1:1 0.333333 \"c aoeu 123\" 2 1 3"))
