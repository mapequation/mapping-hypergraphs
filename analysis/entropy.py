import math


def plogp(p: float) -> float:
    if p > 0:
        return p * math.log2(p)
    return 0


def entropy(p) -> float:
    tot = sum(p)
    return -sum(plogp(p_ / tot) for p_ in p)


def perplexity(p) -> float:
    return 2 ** entropy(p)
