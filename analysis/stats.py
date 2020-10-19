import os
from collections import defaultdict
from itertools import takewhile, dropwhile
from typing import Sequence

from scipy.stats import entropy

from hypergraph.network import Tree


def module_assignments(network: Tree):
    assignments = defaultdict(set)

    for node in network.nodes:
        assignments[node.id].add(node.module)

    return {node_id: len(modules) for node_id, modules in assignments.items()}


def perplexity(network: Tree):
    assignments = defaultdict(lambda: defaultdict(int))
    flow = defaultdict(lambda: defaultdict(float))

    for node in network.nodes:
        assignments[node.id][node.module] += 1
        flow[node.id][node.module] += node.flow

    perplexity_ = {}

    for node_id, node_assignments in assignments.items():
        a = [node_assignments[module_id] for module_id in sorted(node_assignments)]

        perplexity_[node_id] = 2 ** entropy(a, base=2)

    return perplexity_


def summarize(networks: Sequence[Tree]):
    summary = []

    for network in networks:
        name = network.filename

        with open(name) as fp:
            lines = fp.readlines()
            header = takewhile(lambda line: line.startswith("#"), lines)
            # partitioned into 4 levels with 286 top modules
            levels = int(next(filter(lambda line: line.startswith("# partitioned into"), header)).split()[3])
            # codelength 3.11764 bits
            codelength = float(next(filter(lambda line: line.startswith("# codelength"), header)).split()[2])

            states_filename = os.path.splitext(name)[0] + "_states.net"

            with open(states_filename) as states_fp:
                states_lines = states_fp.readlines()

                num_states = len(list(takewhile(lambda line: not line.startswith("*Links"),
                                                dropwhile(lambda line: not line.startswith("# stateId physicalId"),
                                                          states_lines))))

                num_links = len(list(dropwhile(lambda line: not line.startswith("*Links"), states_lines)))

                summary.append((network.pretty_filename, num_states, num_links, levels, codelength))

    for line in summary:
        print("{:26} {} {:5} {} {:.3f}".format(*line))

    return summary
