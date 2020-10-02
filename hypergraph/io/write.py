from typing import List, Sequence, Optional

from hypergraph.network import MultiLayerLink, Link, StateNode, Node


def write_multilayer_network(filename, links: List[MultiLayerLink], nodes: Sequence[Node]):
    with open(filename, "w") as fp:
        fp.write("*Vertices\n")
        fp.writelines("{} \"{}\"\n".format(node.id, node.name) for node in nodes)

        fp.write("*Multilayer\n")
        fp.writelines("{} {} {} {} {}\n".format(e1, u, e2, v, w)
                      for (e1, u), (e2, v), w in links)


def write_bipartite_network(filename,
                            links: List[Link],
                            nodes: Sequence[Node],
                            features: Sequence[Node],
                            states: Optional[Sequence[StateNode]]):
    bipartite_start_id = min(node.id for node in features)

    with open(filename, "w") as fp:
        fp.write("*Vertices\n")
        fp.writelines("{} \"{}\"\n".format(node.id, node.name) for node in nodes)
        fp.writelines("{} \"{}\"\n".format(node.id, node.name) for node in features)

        if states:
            fp.write("*States\n")
            fp.writelines("{} {}\n".format(state.state_id, state.node_id) for state in states)

        fp.write("*Bipartite {}\n".format(bipartite_start_id))
        fp.writelines("{} {} {}\n".format(source, target, w)
                      for source, target, w in links)
