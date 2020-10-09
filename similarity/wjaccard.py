import subprocess


def wjaccard(filename1: str, filename2: str, cmd: str = "wjaccarddist") -> float:
    result = subprocess.run([cmd, filename1, filename2], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        result.check_returncode()
    except subprocess.CalledProcessError:
        raise Exception(result.stderr.decode("utf-8"))

    return float(result.stdout)


if __name__ == "__main__":
    print(wjaccard("output/clique_seed_1.ftree", "output/clique_directed_seed_1.ftree"))
