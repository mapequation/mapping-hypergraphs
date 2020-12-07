import re
from collections import namedtuple, defaultdict
from dataclasses import dataclass
from operator import methodcaller
from typing import Iterable, List, Tuple, Sequence, Mapping, Dict, Set, TextIO

from .network import Node

HyperEdge = namedtuple("HyperEdge", "id, nodes, omega")
Gamma = namedtuple("Gamma", "edge, node, gamma")


class DefaultNodeDict(defaultdict):
    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)

        ret = self[key] = self.default_factory(key)
        return ret


@dataclass
class HyperGraph:
    """
    Format:

        *Vertices # optional
        # id name
        1 "a"
        2 "b"
        3 "c"
        4 "d"
        5 "f"
        *Hyperedges
        # id nodes... omega
        1 1 2 3 10      # e1
        2 3 4 5 20      # e2
        *Weights # optional, missing weights defaults to gamma = 1.0
        # edge node gamma
        1 1 1      # gamma_e1(a)
        1 2 1      # gamma_e1(b)
        1 3 2      # gamma_e1(c)
        2 3 1      # gamma_e2(c)
        2 4 1      # gamma_e2(d)
        2 5 2      # gamma_e2(f)
    """
    nodes: List[Node]
    edges: List[HyperEdge]
    weights: List[Gamma]

    def __iter__(self):
        return iter((self.nodes, self.edges, self.weights))

    def write(self, fp: TextIO):
        fp.write("*Vertices\n")
        fp.write("# id name\n")
        fp.writelines(f"{node.id} \"{node.name}\"\n"
                      for node in sorted(self.nodes))

        fp.write("*Hyperedges\n")
        fp.write("# id nodes... omega\n")
        fp.writelines(f"{edge.id} {' '.join(map(str, (node.id for node in edge.nodes)))} {edge.omega}\n"
                      for edge in sorted(self.edges))

        fp.write("*Weights\n")
        fp.write("# edge node gamma\n")
        fp.writelines(f"{weight.edge} {weight.node.id} {weight.gamma}\n"
                      for weight in sorted(self.weights)
                      if weight.gamma != 1)

    @classmethod
    def from_iter(cls, lines: Iterable[str]):
        nodes_lines, edges_lines, weights_lines = read(lines)

        nodes = parse_nodes(nodes_lines)

        if len(nodes) == 0:
            nodes = DefaultNodeDict(lambda node_id: Node(node_id, str(node_id)))

        edges = parse_edges(edges_lines, nodes)

        nodes = filter_dangling(nodes, edges)

        if len(weights_lines):
            weights = parse_weights(weights_lines, nodes)

            weights.extend(missing_default_weights(edges, weights))
        else:
            weights = default_weights(edges)

        return cls(list(nodes.values()), edges, weights)


def read(lines) -> Tuple[List[str], List[str], List[str]]:
    lines = (line.strip() for line in lines)
    lines = (line for line in lines if not line.startswith("#"))

    nodes = []
    edges = []
    weights = []

    context = None

    for line in lines:
        if line.startswith('*'):
            context = line.lower()
            continue
        elif context == "*vertices":
            nodes.append(line)
        elif context == "*hyperedges":
            edges.append(line)
        elif context == "*weights":
            weights.append(line)

    return nodes, edges, weights


def filter_dangling(nodes: Mapping[int, Node], edges: Sequence[HyperEdge]) -> Dict[int, Node]:
    referenced_nodes = {node.id for edge in edges for node in edge.nodes}

    return {node.id: node for node in nodes.values()
            if node.id in referenced_nodes}


def parse_nodes(lines: Sequence[str]) -> Dict[int, Node]:
    nodes = {}

    for line in lines:
        m = re.match(r"(\d+) \"(.+)\"", line)
        if m:
            node_id, name = m.groups()
            node_id = int(node_id)
            nodes[node_id] = Node(node_id, name)

    return nodes


def parse_edges(lines: Sequence[str], nodes: Mapping[int, Node]) -> List[HyperEdge]:
    lines_ = (tuple(map(int, first)) + (float(omega),)
              for *first, omega in map(methodcaller("split"), lines))

    return [HyperEdge(edge_id, frozenset(nodes[node_id] for node_id in node_ids), omega)
            for edge_id, *node_ids, omega in lines_]


def parse_weights(lines: Sequence[str], nodes: Mapping[int, Node]) -> List[Gamma]:
    lines_ = (tuple(map(int, ids)) + (float(gamma),)
              for *ids, gamma in map(methodcaller("split"), lines))

    return [Gamma(edge, nodes[node_id], gamma)
            for edge, node_id, gamma in lines_]


def default_weights(edges: Sequence[HyperEdge], weight: float = 1.0) -> List[Gamma]:
    return [Gamma(edge.id, node, weight)
            for edge in edges for node in edge.nodes]


def missing_default_weights(edges: Sequence[HyperEdge], weights: Sequence[Gamma], weight: float = 1.0) -> List[Gamma]:
    return [Gamma(edge, node, weight) for edge, node in missing_weights(edges, weights)]


def missing_weights(edges: Sequence[HyperEdge], weights: Sequence[Gamma]) -> Set[Tuple[int, Node]]:
    found_weights = {(weight.edge, weight.node) for weight in weights}

    all_nodes = {(edge.id, node) for edge in edges for node in edge.nodes}

    return all_nodes - found_weights


def remove_simple_hyperedges(hypergraph: HyperGraph) -> HyperGraph:
    nodes, edges, weights = hypergraph

    edges_ = [edge for edge in edges if len(edge.nodes) > 1]
    nodes_ = set()
    weights_ = []

    for edge in edges_:
        nodes_.update(edge.nodes)
        weights_.extend(weight for weight in weights
                        if weight.edge == edge.id)

    return HyperGraph(list(nodes_), edges_, weights_)
