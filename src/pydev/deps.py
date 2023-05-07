import subprocess
from pathlib import Path

import tomlkit


def attachToArgparser(parser):
    parser.description = "routines for collecting package dependencies."
    parser.add_argument(
        "-s",
        "--src",
        type=str,
        default=".",
        help="source to collect dependencies for. the given folder should contain a src subfolder",
    )


def main(args):
    print(f"checking {Path(args['src']).resolve()}")
    subprocess.call(["pipreqs", args["src"], "--force"])
    p = Path(args["src"]) / "requirements.txt"
    reqs = open(p, "r").readlines()

    # first, check if we added any of the requirements to the git-dependencies in pyproject.toml.
    # if so, replace them with the git-reqs.
    # then, change the version requirements to "compatible (~=)"
    for ln, req in enumerate(reqs):
        reqs[ln] = req.replace("==", "~=")

    # then, add all elements to pyproject.toml
    f = Path(args["src"]) / "pyproject.toml"
    pyproject = tomlkit.load(open(f, "r"))
    pyproject.pop("dependencies")
    pyproject.append("dependencies", [x.strip() for x in reqs])
    tomlkit.dump(pyproject, open(f, "w"))
    print(f"wrote dependencies to {f}")

    # then, delete reqs.txt
    print(f"deleting {p}")
    p.unlink()
    return 0
