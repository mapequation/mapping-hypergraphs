from itertools import dropwhile
from unicodedata import normalize

from scholarly import scholarly, ProxyGenerator

pg = ProxyGenerator()

pg.Tor_Internal(tor_cmd="/usr/local/bin/tor")

scholarly.use_proxy(pg)


def get_google_scholar_citations(title: str, first_author: str) -> int:
    print("{}: {} -> ".format(first_author, title), end="")

    *_, last_name = first_author.split()

    query = "{} {}".format(title.rstrip("."), last_name)

    try:
        results = scholarly.search_pubs(query, patents=False)
    except Exception:
        print("no match")
        return -1

    for result in results:
        found_author = normalize("NFD", result.bib["author"][0]) \
            .encode("ascii", "ignore") \
            .decode("ascii")

        if last_name.lower() in found_author.lower():
            print("{}: {}".format(result.bib["title"], result.bib["author"][0]))
            return int(result.bib["cites"])

    print("no match")
    return -1


filename = "data/citations.txt"
citations = {}

with open(filename) as fp:
    lines = dropwhile(lambda line: not line.startswith("*Hyperedges"), fp.readlines())
    next(lines)
    for line in lines:
        edge_id, *node_ids, omega = line.split()
        citations[int(edge_id)] = int(omega)


def get_citations(title: str, first_author: str, edge_id: int) -> int:
    try:
        return citations[edge_id]
    except KeyError:
        return get_google_scholar_citations(title, first_author)
