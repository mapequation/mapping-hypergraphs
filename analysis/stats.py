import os
from collections import defaultdict
from itertools import takewhile, dropwhile
from statistics import mean
from typing import Sequence

import pandas as pd

from hypergraph.network import Tree


def summarize(networks: Sequence[Tree]) -> pd.DataFrame:
    summary = defaultdict(list)

    for network in networks:
        states_filename = os.path.splitext(network.filename)[0] + "_states.net"

        with open(states_filename) as states_fp:
            states_lines = states_fp.readlines()

        num_states = len(list(takewhile(lambda line: not line.startswith("*Links"),
                                        dropwhile(lambda line: not line.startswith("# stateId physicalId"),
                                                  states_lines)))) - 1

        num_links = len(list(dropwhile(lambda line: not line.startswith("*Links"), states_lines))) - 1

        summary["network"].append(network.pretty_filename)
        summary["num states"].append(num_states)
        summary["num links"].append(num_links)
        summary["levels"].append(network.levels)
        summary["top modules"].append(network.num_top_modules)
        summary["codelength"].append(network.codelength)
        summary["mean assignments"].append(mean(network.assignments.values()))
        summary["mean eff. assignments"].append(mean(network.effective_assignments.values()))

    return pd.DataFrame(data=summary)
