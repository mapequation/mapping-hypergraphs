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
    node_id: int
    state_id: Optional[int] = None
    layer_id: Optional[int] = None
    is_bipartite: bool = False

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

    @property
    def is_multilayer(self) -> bool:
        return self.layer_id is not None

    @classmethod
    def from_str(cls, line: str, is_bipartite=False):
        name, state_id, layer_id = None, None, None

        match = re.search(r" \"([\w\s\-\']+)\" ", line.strip())

        if match:
            name = match.group(1)
            line = re.sub(r" \"[\w\s\-\']+\"", "", line)

        path, flow, *ids = line.split()
        path, flow, ids = tuple(map(int, path.split(":"))), float(flow), list(map(int, ids))

        if len(ids) == 2:
            state_id, node_id = ids
        elif len(ids) == 3:
            if is_bipartite:
                raise Exception("Parsed as bipartite but found layer id!")
            state_id, node_id, layer_id = ids
        else:
            node_id = ids[0]

        return TreeNode(path, flow, name if name else str(node_id), node_id, state_id, layer_id, is_bipartite)


NodeFilter = Callable[[str], bool]


def is_feature_node(line: str) -> bool:
    return "hyperedge" in line.lower()


def tree_nodes(lines: Iterable[str],
               bipartite=False,
               node_filter: NodeFilter = is_feature_node) -> List[TreeNode]:
    tree_data = lambda line: not line.startswith("*")
    comment = lambda line: line.startswith("#")

    return list(TreeNode.from_str(line, bipartite)
                for line in filterfalse(node_filter, takewhile(tree_data, dropwhile(comment, lines))))


if __name__ == "__main__":
    node = TreeNode.from_str("1:1:2 0.333333 \"c aoeu\" 1")
    print(node.module)
    print(TreeNode.from_str("1:1 0.333333 \"c aoeu\" 2 1"))
    print(TreeNode.from_str("1:1 0.333333 \"c aoeu 123\" 2 1 3"))
