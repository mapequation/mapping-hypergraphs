import os
from collections import defaultdict
from itertools import takewhile, dropwhile
from typing import Sequence

import pandas as pd
from scipy.stats import entropy

from hypergraph.network import Tree


def assignments(network: Tree) -> pd.DataFrame:
    assignments_ = defaultdict(set)

    for node in network.nodes:
        assignments_[node.id].add(node.module)

    assignments_ = {node_id: len(modules)
                    for node_id, modules in assignments_.items()}

    return pd.DataFrame(data={network.pretty_filename: sorted(assignments_.values(), reverse=True)})


def perplexity(x) -> float:
    return 2 ** entropy(x, base=2)


def effective_assignments(network: Tree) -> pd.DataFrame:
    assignments_ = defaultdict(lambda: defaultdict(int))

    for node in network.nodes:
        assignments_[node.id][node.module] += 1

    perplexity_ = {node_id: perplexity(list(node_assignments.values()))
                   for node_id, node_assignments in assignments_.items()}

    return pd.DataFrame(data={network.pretty_filename: sorted(perplexity_.values(), reverse=True)})


def summarize(networks: Sequence[Tree]) -> pd.DataFrame:
    summary = defaultdict(list)

    for network in networks:
        states_filename = os.path.splitext(network.filename)[0] + "_states.net"

        with open(states_filename) as states_fp:
            states_lines = states_fp.readlines()

        num_states = len(list(takewhile(lambda line: not line.startswith("*Links"),
                                        dropwhile(lambda line: not line.startswith("# stateId physicalId"),
                                                  states_lines))))

        num_links = len(list(dropwhile(lambda line: not line.startswith("*Links"), states_lines)))

        summary["network"].append(network.pretty_filename)
        summary["num states"].append(num_states)
        summary["num links"].append(num_links)
        summary["levels"].append(network.levels)
        summary["top modules"].append(network.num_top_modules)
        summary["codelength"].append(network.codelength)

    return pd.DataFrame(data=summary)
