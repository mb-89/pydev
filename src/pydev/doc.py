"""Build the documentation for this package package."""

import os
import shutil
import subprocess
from pathlib import Path

import tomlkit


def attachToArgparser(parser):
    """Attach a subparser for this module to the given parser."""
    parser.description = globals()["__doc__"]
    parser.add_argument("-s", "--src", type=str, default=".", help="source to build doc for")


def main(args):
    """Execute this modules function with the args defined in attachToArgparser."""
    dp = Path(args["src"]) / "doc"
    shutil.rmtree(dp, ignore_errors=True)
    dp.mkdir(exist_ok=True)  # exist ok only needed for testing

    tmp = Path(args["src"]) / "pyproject.toml"
    pyproject = tomlkit.load(open(tmp, "r"))

    modname = pyproject["project"]["name"]
    auth = ", ".join(x["name"] for x in pyproject["project"]["authors"])
    v = pyproject["project"]["version"]

    errno = subprocess.call(
        [
            "sphinx-quickstart.exe",
            "--no-sep",
            "-p",
            modname,
            "-a",
            f"{auth}",
            "-v",
            v,
            "-r",
            v,
            "-l",
            "en",
            "--ext-autodoc",
            "--ext-viewcode",
            "--ext-todo",
        ],
        cwd=dp,
    )
    if errno:  # pragma: no cover /generic edge case
        return errno

    conf = open(dp / "conf.py", "r").readlines()
    conf.append('html_theme = "sphinx_rtd_theme"')
    for idx, x in enumerate(conf):
        if x.startswith("""version = '"""):
            ver = v
            conf[idx] = f"""version = '{ver}'\n"""
            conf[idx + 1] = f"""release = '{ver}'\n"""
            break
    open(dp / "conf.py", "w").write("".join(conf))
    conf = open(dp / "index.rst", "r").read()
    conf = conf.replace("Indices and tables", f"   {modname}\n\n" "Indices and tables")
    open(dp / "index.rst", "w").write(conf)
    errno = subprocess.call(
        ["sphinx-apidoc", "--module-first", "-o", "./doc", f"./src/{modname}"], cwd=args["src"]
    )
    if errno:  # pragma: no cover /generic edge case
        return errno
    errno = subprocess.call([r".\doc\make.bat", "html"], cwd=args["src"])
    if errno:  # pragma: no cover /generic edge case
        return errno
    output = Path(args["src"]) / "doc" / "_build" / "html" / "index.html"
    os.system(str(output))
    return 0
