import os


def pretty_filename(filename: str) -> str:
    basename = os.path.basename(filename)
    name, _ = os.path.splitext(basename)
    return name.replace("_", " ")
