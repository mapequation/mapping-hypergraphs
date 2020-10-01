from infomap import Infomap


def create_network(node_pairs):
    intra = []
    inter = []

    print("[multilayer] creating multilayer... ", end="")
    for e1, u, e2, v, w in node_pairs:
        if e1 == e2:
            links = intra
        else:
            links = inter

        # layer_id node_id layer_id node_id weight
        links.append((e1.id, u.id, e2.id, v.id, w))

    links = [((e1, u), (e2, v), w)
             for links in (intra, inter)
             for e1, u, e2, v, w in sorted(links, key=lambda link: link[0])]

    print("done")
    return links


def run_infomap(filename, links, nodes):
    print("[infomap] running infomap on multilayer network... ", end="")
    im = Infomap("-d -N5 --silent")
    im.set_names(nodes)
    im.add_multilayer_links(links)
    im.run()
    im.write_flow_tree(filename, states=True)
    print("done")
    print("[infomap] codelength {}".format(im.codelength))
    print("[infomap] num top modules {}".format(im.num_non_trivial_top_modules))
