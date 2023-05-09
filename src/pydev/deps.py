"""Collect package dependencies and store them in pyroject.toml."""

import configparser
import io
import subprocess
import time
from pathlib import Path

import tomlkit


def attachToArgparser(parser):
    """Attach a subparser for this module to the given parser."""
    parser.description = globals()["__doc__"]
    parser.add_argument(
        "-s",
        "--src",
        type=str,
        default=".",
        help="source to collect dependencies for. the given folder should contain a src subfolder",
    )


def main(args):
    """Execute this modules function with the args defined in attachToArgparser."""
    print(f"checking {Path(args['src']).resolve()}")
    subprocess.call(["pipreqs", args["src"] + "/src", "--force"])
    p = Path(args["src"]) / "src" / "requirements.txt"
    try:
        reqs = open(p, "r").readlines()
    except FileNotFoundError:  # pragma: no cover
        time.sleep(1)  # sometimes the file creation takes some time..
        reqs = open(p, "r").readlines()

    # first, check if we added any of the requirements to the git-dependencies in pyproject.toml.
    # if so, replace them with the git-reqs.
    # then, change the version requirements to "compatible (~=)"
    for ln, req in enumerate(reqs):
        reqs[ln] = req.replace("==", "~=")

    # then, add all elements to pyproject.toml
    f = Path(args["src"]) / "pyproject.toml"
    pyproject = tomlkit.load(open(f, "r"))

    # enter the dependencies in the main cfg
    deps = [x.strip() for x in reqs]
    pyproject.pop("dependencies")
    pyproject.append("dependencies", deps)

    # also enter the dependencies in the tox subconfig
    deps.append("pytest")
    toxstr = pyproject["tool"]["tox"].pop("legacy_tox_ini")
    toxcfg = configparser.ConfigParser()
    toxcfg.read_string(toxstr)
    toxcfg["testenv"]["deps"] = "\n" + "\n\t".join(deps)
    with io.StringIO() as fp:
        toxcfg.write(fp)
        fp.seek(0)
        newtoxstr = fp.read()
    tmp = '"""\n' + newtoxstr + '\n"""\n'
    tmp = tmp.replace("\t", "    ")
    open("tmp", "w").write(tmp)
    # pyproject["tool"]["tox"]["legacy_tox_ini"] = tmp
    # tomlkit.dump(pyproject, open(f, "w"))
    txt1 = tomlkit.dumps(pyproject)
    txt2 = open("tmp", "r").read()
    alltxt = txt1 + "legacy_tox_ini = " + txt2
    open(f, "w").write(alltxt)
    print(f"wrote dependencies to {f}")

    # then, delete reqs.txt
    print(f"deleting {p}")
    p.unlink()
    Path("tmp").unlink()
    return 0
