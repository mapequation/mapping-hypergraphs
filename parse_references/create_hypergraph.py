from parse_references import parse


def hypergraph(refs, outfile):
    unique_authors = {author for coauthors in refs for author in coauthors}
    authors = {i + 1: author for i, author in enumerate(unique_authors)}
    author_ids = {author: i for i, author in authors.items()}

    outfile.write("*Vertices\n")
    outfile.writelines("{} \"{}\"\n".format(i, author) for i, author in authors.items())

    articles = {i + 1: coauthors for i, coauthors in enumerate(refs)}
    articles_author_ids = {i: tuple(author_ids[author] for author in coauthors)
                           for i, coauthors in articles.items()}

    outfile.write("*Hyperedges\n")
    outfile.writelines("{} {} 1\n".format(i, " ".join(map(str, author_ids)))
                       for i, author_ids in articles_author_ids.items())

    outfile.write("*Weights\n")

    for i, author_ids in articles_author_ids.items():
        num_coauthors = len(author_ids)

        if num_coauthors == 1:
            weights = (2,)
        else:
            weights = (2,) + (1,) * (num_coauthors - 2) + (2,)

        outfile.writelines("{} {} {}\n".format(i, author_id, weight)
                           for author_id, weight in zip(author_ids, weights))


if __name__ == "__main__":
    with open("data/networks-beyond-pairwise-interactions-references.tex", "r") as texfile:
        with open("data/networks-beyond-pairwise-interactions.txt", "w") as outfile:
            hypergraph(parse(texfile.read()), outfile)
