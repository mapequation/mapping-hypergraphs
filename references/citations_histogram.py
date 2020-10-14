import statistics
from itertools import dropwhile
from typing import Sequence

import matplotlib.pyplot as plt
import seaborn as sns

sns.set()


def citations_hist(lines: Sequence[str]):
    hyperedges = dropwhile(lambda line: not line.startswith("*Hyperedges"), lines)
    next(hyperedges)

    citations = tuple(int(line.split()[-1]) for line in hyperedges)

    print("Mode:", statistics.mode(citations))
    print("Mean:", statistics.mean(citations))
    print("Median:", statistics.median(citations))

    plt.figure()
    sns.displot(citations, bins=30)
    plt.title("Citations")
    plt.show()


def main(filename: str = "data/citations.txt"):
    with open(filename) as fp:
        citations_hist(fp.readlines())


if __name__ == "__main__":
    main()
