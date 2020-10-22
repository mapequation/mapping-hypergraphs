from collections import namedtuple
from dataclasses import dataclass
from operator import attrgetter
from typing import Tuple, List, Union, TextIO

Node = namedtuple("Node", "id, name")
StateNode = namedtuple("StateNode", "state_id, node_id")

Link = Tuple[int, int, float]
MultiLayerLink = Tuple[Tuple[int, int], Tuple[int, int], float]


@dataclass
class Network:
    nodes: List[Node]
    links: List[Link]

    def apply(self, infomap):
        infomap.add_nodes(self.nodes)
        infomap.add_links(self.links)

    def write(self, fp: TextIO):
        self._write_nodes(fp)
        self._write_links(fp)

    def _write_nodes(self, fp: TextIO):
        fp.write("*Vertices\n")
        fp.writelines(f"{node.id} \"{node.name}\"\n" for node in self.nodes)

    def _write_links(self, fp: TextIO):
        fp.write("*Edges\n")
        fp.writelines(f"{source} {target} {w}\n"
                      for source, target, w in self.links)


@dataclass
class StateNetwork(Network):
    states: List[StateNode]

    def apply(self, infomap):
        infomap.set_names(self.nodes)
        infomap.add_state_nodes(self.states)
        infomap.add_links(self.links)

    def write(self, fp: TextIO):
        self._write_nodes(fp)
        self._write_states(fp)
        self._write_links(fp)

    def _write_states(self, fp: TextIO):
        fp.write("*States\n")
        fp.writelines(f"{state.state_id} {state.node_id}\n"
                      for state in self.states)


@dataclass
class BipartiteNetwork(Network):
    features: List[Node]

    def apply(self, infomap):
        super().apply(infomap)
        infomap.add_nodes(self.features)
        infomap.bipartite_start_id = self.bipartite_start_id

    @property
    def bipartite_start_id(self) -> int:
        return min(map(attrgetter("id"), self.features))

    def _write_nodes(self, fp: TextIO):
        super()._write_nodes(fp)
        fp.writelines(f"{node.id} \"{node.name}\"\n"
                      for node in self.features)

    def _write_links(self, fp: TextIO):
        fp.write(f"*Bipartite {self.bipartite_start_id}\n")
        fp.writelines(f"{source} {target} {w}\n"
                      for source, target, w in self.links)


@dataclass
class BipartiteStateNetwork(BipartiteNetwork, StateNetwork):
    def apply(self, infomap):
        infomap.set_names(self.nodes)
        infomap.set_names(self.features)
        infomap.add_state_nodes(self.states)
        infomap.add_links(self.links)
        infomap.bipartite_start_id = self.bipartite_start_id


@dataclass
class MultilayerNetwork(Network):
    links: List[MultiLayerLink]

    def apply(self, infomap):
        infomap.set_names(self.nodes)
        infomap.add_multilayer_links(self.links)

    def _write_links(self, fp: TextIO):
        fp.write("*Multilayer\n")
        fp.writelines(f"{e1} {u} {e2} {v} {w}\n"
                      for (e1, u), (e2, v), w in self.links)


def network_from_file(filename: str) -> Union[Network, StateNetwork]:
    with open(filename) as fp:
        lines = fp.readlines()

    nodes, states, links = [], [], []

    context = None

    for line in lines:
        line = line.strip()

        if line.startswith("*"):
            context = line
            continue
        if line.startswith("#"):
            continue

        if context == "*Vertices":
            split_index = line.index(" ")
            id_, name = line[:split_index], line[split_index + 1:]
            name = name.strip("\"")
            nodes.append(Node(int(id_), name))
        elif context == "*States":
            state_id, node_id = map(int, line.split())
            states.append(StateNode(state_id, node_id))
        elif context == "*Links":
            source, target, weight = line.split()
            links.append((int(source), int(target), float(weight)))

    if len(states):
        return StateNetwork(nodes, links, states)

    return Network(nodes, links)
