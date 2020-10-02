from typing import Callable

from infomap import Infomap

InfomapCallback = Callable[[Infomap], None]


def run_infomap(filename, callback: InfomapCallback):
    print("[infomap] running infomap... ", end="")
    im = Infomap("-d -N5 --silent")
    callback(im)
    im.run()
    im.write_flow_tree(filename, states=True)
    print("done")
    print("[infomap] codelength {}".format(im.codelength))
    print("[infomap] num top modules {}".format(im.num_non_trivial_top_modules))