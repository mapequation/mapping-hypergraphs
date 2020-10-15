import os
from collections import defaultdict
from itertools import takewhile, dropwhile
from typing import Sequence

from analysis import entropy
from analysis.tree import Tree


def overlap(network: Tree):
    module_assignments = defaultdict(lambda: defaultdict(int))

    for node in network.nodes:
        module_assignments[node.id][node.module] += 1

    overlaps = {}

    for node_id, assignments in module_assignments.items():
        num_assignments = len(assignments.keys())
        tot_assignments = sum(assignments.values())

        if tot_assignments == 1:
            overlaps[node_id] = 0
            continue

        overlaps[node_id] = (num_assignments - 1) / (tot_assignments - 1)

    return overlaps


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

    for node_id, a in assignments.items():
        perplexity_[node_id] = entropy.perplexity(a.values())

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
