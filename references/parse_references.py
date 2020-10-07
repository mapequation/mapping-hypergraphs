import re
from unicodedata import normalize


def parse(texfile, verbose=False):
    tex = texfile.read()
    refs = list(map(lambda r: r.split("\n"),
                    tex.split("\n\n")))

    references = []

    authors_map = {
        "arenas": "alex arenas",
        "barabasi": "albert-laszlo barabasi",
        "newman": "m e j newman",
        "latora": "vito latora",
        "sendina-nadal": "irene sendina-nadal",
        "diaz-guilera": "albert diaz-guilera",
        'criado': 'regino criado',
        'pikovsky': 'arkady s pikovsky',
        'edelsbrunner': 'herbert edelsbrunner',
        'ghoshal': 'gourab ghoshal',
        'moreno': 'yamir moreno',
        'alon': 'uri alon',
        'zou': 'yong zou',
        'rosenblum': 'michael g rosenblum',
        'murali': 't m murali',
        'guan': 'shuguang guan',
        'mendes': 'j f f mendes',
        'chavez': 'mario chavez',
        'abbott': 'laurence f abbott',
        'kurths': 'jurgen kurths',
        'maynard smith': 'john maynard smith',
        'romance': 'miguel romance',
        'boccaletti': 'stefano boccaletti',
        'strogatz': 'steven h strogatz',
        'axelrod': 'robert axelrod',
        'ghrist': 'robert ghrist',
        'dorogovtsev': 'sergey n dorogovtsev',
        'krawiecki': 'andrzej krawiecki',
        'foster': 'brian l foster',
        'berec': 'vesna berec',
        'wang': 'zhen wang',
        'mangan': 'shmoolik mangan',
        "miller mcpherson": "j miller mcpherson",
        "sole": "ricard v sole",
        "shen-orr": "shai s shen-orr",
        "benson": "austin r benson",
        "gleich": "david f gleich",
        "leskovec": "jurij leskovec",
        "chodrow": "philip s chodrow",
        "duval": "art m duval",
        "granovetter": "mark s granovetter",
        "philippa pattison": "philippa e pattison",
        "robins": "garry l robins",
        "frank": "loren m frank",
        "ball": "frank g ball",
        "aldous": "david j aldous",
        "sizemore": "ann e sizemore",
        "torres": "joaquin j torres",
        "mirasso": "claudio r mirasso",
        "perc": "matjaz perc",
        "floria": "luis mario floria",
        "vandermeer": "john h vandermeer",
        "klivans": "caroline j klivans"
    }

    for ref in refs:
        authors = None
        bibitem_parsed = False
        authors_parsed = False

        for line in ref:
            if line.startswith("\\bibitem"):
                # is reference label in the first line?
                bibitem_parsed = re.search(r"\[.+]{\S+?}", line)
                continue

            if not bibitem_parsed:
                if re.search(r"[^\\]+]{\S+?}$", line):
                    # label was in the second line
                    # next line should be author list
                    bibitem_parsed = True
                continue

            if authors_parsed or line.startswith(r"\newblock"):
                authors_parsed = True
                continue

            if not authors_parsed:
                if authors:
                    authors += " " + line
                else:
                    authors = line

        if authors:
            # normalize line
            authors = normalize("NFD", authors) \
                .encode("ascii", "ignore") \
                .decode("ascii")

            authors = authors.strip() \
                .lower() \
                .rstrip(".") \
                .replace("~", " ") \
                .replace(".", " ")

            authors = re.sub(r",? and ", r", ", authors)
            authors = re.sub(r",? et\.? al\.?", "", authors)

            # remove latex stuff
            authors = re.sub(r"\s+", " ", authors)
            authors = re.sub(r"\\v{z}", "z", authors)
            authors = re.sub(r"{\\.(.)+?}", r"\1", authors)
            authors = re.sub(r"{(.+?)}", r"\1", authors)
            authors = re.sub(r"\\.", "", authors)

            author_list = authors.split(", ")

            # re-map common variants
            for i, name in enumerate(author_list):
                for last_name, complete_name in authors_map.items():
                    if name != complete_name \
                            and name[0] == complete_name[0] \
                            and name.endswith(" " + last_name):
                        author_list[i] = complete_name
                        if verbose:
                            print("{} -> {}".format(name, complete_name))
                        break

            references.append(tuple(author_list))

    unique_authors = set()

    for coauthors in references:
        unique_authors.update(coauthors)

    if verbose:
        print("-----------------------------")
    print("Parsed {}/{} references".format(len(references), len(refs)))
    print("Authors: {}".format(len(unique_authors)))

    return references


if __name__ == "__main__":
    with open("data/networks-beyond-pairwise-interactions-references.tex") as fp:
        parse(fp.read())
