import re
from dataclasses import dataclass
from itertools import filterfalse, takewhile, dropwhile
from typing import Tuple, Optional, Iterable, List

Path = Tuple[int, ...]


@dataclass
class TreeNode:
    path: Path
    flow: float
    name: str
    node_id: int
    state_id: Optional[int] = None
    layer_id: Optional[int] = None

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
    def module(self) -> Tuple[int, ...]:
        return self.path[:-1]

    @classmethod
    def from_str(cls, line: str):
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
            state_id, node_id, layer_id = ids
        else:
            node_id = ids[0]

        return TreeNode(path, flow, name if name else str(node_id), node_id, state_id, layer_id)


def tree_nodes(lines: Iterable[str]) -> List[TreeNode]:
    tree_data = lambda line: not line.startswith("*")
    comment = lambda line: line.startswith("#")
    feature_nodes = lambda line: "hyperedge" in line.lower()

    return list(map(TreeNode.from_str,
                    filterfalse(feature_nodes, takewhile(tree_data, dropwhile(comment, lines)))))


if __name__ == "__main__":
    node = TreeNode.from_str("1:1:2 0.333333 \"c aoeu\" 1")
    print(node.module)
    print(TreeNode.from_str("1:1 0.333333 \"c aoeu\" 2 1"))
    print(TreeNode.from_str("1:1 0.333333 \"c aoeu 123\" 2 1 3"))
