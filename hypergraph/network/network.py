from collections import namedtuple
from dataclasses import dataclass
from operator import attrgetter
from typing import Tuple, Optional, List

Node = namedtuple("Node", "id, name")
StateNode = namedtuple("StateNode", "state_id, node_id")

Link = Tuple[int, int, float]
MultiLayerLink = Tuple[Tuple[int, int], Tuple[int, int], float]


@dataclass
class Network:
    nodes: List[Node]
    links: List[Link]

    def write(self, filename):
        with open(filename, "w") as fp:
            self._write_nodes(fp)
            self._write_links(fp)

    def _write_nodes(self, fp):
        fp.write("*Vertices\n")
        fp.writelines("{} \"{}\"\n".format(node.id, node.name) for node in self.nodes)

    def _write_links(self, fp):
        fp.write("*Edges\n")
        fp.writelines("{} {} {}\n".format(source, target, w)
                      for source, target, w in self.links)


@dataclass
class BipartiteNetwork(Network):
    features: List[Node]
    states: Optional[List[StateNode]] = None

    @property
    def bipartite_start_id(self) -> int:
        return min(map(attrgetter("id"), self.features))

    def _write_nodes(self, fp):
        super()._write_nodes(fp)

        fp.writelines("{} \"{}\"\n".format(node.id, node.name)
                      for node in self.features)

        if self.states:
            fp.write("*States\n")
            fp.writelines("{} {}\n".format(state.state_id, state.node_id)
                          for state in self.states)

    def _write_links(self, fp):
        fp.write("*Bipartite {}\n".format(self.bipartite_start_id))
        fp.writelines("{} {} {}\n".format(source, target, w)
                      for source, target, w in self.links)


@dataclass
class MultilayerNetwork(Network):
    links: List[MultiLayerLink]

    def _write_links(self, fp):
        fp.write("*Multilayer\n")
        fp.writelines("{} {} {} {} {}\n".format(e1, u, e2, v, w)
                      for (e1, u), (e2, v), w in self.links)
