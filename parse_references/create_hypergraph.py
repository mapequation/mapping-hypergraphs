from parse_references import parse


def hyperedge(edge_id, node_ids):
    ids = " ".join(map(str, node_ids))
    omega = 1
    return "{} {} {}\n".format(edge_id, ids, omega)


def weight(edge_id, node_id, gamma):
    return "{} {} {}\n".format(edge_id, node_id, gamma)


def weights(n):
    # if n == 1:
    #     gamma = (2,)
    # else:
    #     gamma = (3,) + (1,) * (n - 2) + (3,)
    gamma = (1,) * n

    return gamma


def hypergraph(refs, outfile):
    print("Writing vertices... ", end="")
    unique_authors = {author for coauthors in refs for author in coauthors}
    authors = {i + 1: author for i, author in enumerate(unique_authors)}
    author_ids = {author: i for i, author in authors.items()}

    outfile.write("*Vertices\n")
    outfile.writelines("{} \"{}\"\n".format(node_id, name) for node_id, name in authors.items())
    print("done")

    print("Writing hyperedges... ", end="")
    articles = {i + 1: coauthors for i, coauthors in enumerate(refs)}
    articles_author_ids = {edge_id: tuple(author_ids[author] for author in coauthors)
                           for edge_id, coauthors in articles.items()}

    outfile.write("*Hyperedges\n")
    outfile.writelines(hyperedge(i, node_ids)
                       for i, node_ids in articles_author_ids.items())
    print("done")

    print("Writing weigths... ", end="")
    outfile.write("*Weights\n")
    outfile.writelines(weight(i, node_id, w)
                       for i, ids in articles_author_ids.items()
                       for node_id, w in zip(ids, weights(len(ids))))
    print("done")


if __name__ == "__main__":
    with open("data/networks-beyond-pairwise-interactions-references.tex", "r") as texfile:
        with open("data/networks-beyond-pairwise-interactions.txt", "w") as outfile:
            hypergraph(parse(texfile.read()), outfile)
