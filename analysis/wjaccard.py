import subprocess
from collections import defaultdict
from itertools import combinations_with_replacement
from typing import Sequence

import numpy as np
import pandas as pd

from analysis.tree import pretty_filename


def wjaccard(filename1: str, filename2: str, cmd: str = "wjaccarddist") -> float:
    result = subprocess.run([cmd, filename1, filename2], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        result.check_returncode()
    except subprocess.CalledProcessError:
        raise Exception(result.stderr.decode("utf-8"))

    return float(result.stdout)


def weighted_jaccard_dist(filenames: Sequence[str]) -> pd.DataFrame:
    dist = np.zeros(shape=(len(filenames),) * 2)

    index = defaultdict(lambda: len(index))

    for filename1, filename2 in combinations_with_replacement(filenames, 2):
        j = index[pretty_filename(filename1)]
        i = index[pretty_filename(filename2)]

        dist[i, j] = 1 - wjaccard(filename1, filename2)

    return pd.DataFrame(data=dist, columns=list(index.keys()))


if __name__ == "__main__":
    print(wjaccard("output/clique_seed_1.ftree", "output/clique_directed_seed_1.ftree"))
