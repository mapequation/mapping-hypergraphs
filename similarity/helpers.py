import os
import re


def pretty_filename(filename: str) -> str:
    basename = os.path.basename(filename)
    name, _ = os.path.splitext(basename)
    name = re.sub(r"_seed_\d+$", "", name)
    return name.replace("_", " ")
