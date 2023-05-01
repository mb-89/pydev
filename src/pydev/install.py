import importlib.metadata as md
import subprocess
import sys
from pathlib import Path

import tomlkit


def attachToArgparser(parser):
    parser.description = "routines for installing a given module"
    parser.add_argument("-d", "--dev", action="store_true", help="installs in dev mode")
    parser.add_argument("-s", "--src", type=str, default=".", help="source to install from")


def main(args):
    errno = install(args)
    if errno:
        return

    addExecutable(args)
    addGitPrecommitHook(args)


def addGitPrecommitHook(args):
    if not args["dev"]:
        return
    checkgit = ["git", "rev-parse", "--show-toplevel"]
    ret = subprocess.run(checkgit, capture_output=True).stdout.decode("cp1252").strip()
    if not ret:
        return
    gitpath = Path(ret)
    if not gitpath.is_dir():
        return
    exec_fn = gitpath / ".git" / "hooks" / "pre-commit"
    exec_content = f"pydev prune"
    if exec_fn.is_file():
        print(f"a pre-commit hook already exists @ {exec_fn}. Hook was not changed!")
    open(exec_fn, "w").write(exec_content)


def addExecutable(args):
    metadata = md.metadata(__name__.split(".")[0])
    name = metadata["name"]
    f = Path(args["src"]) / "pyproject.toml"
    if not f.is_file():
        return
    pyproject = tomlkit.load(open(f, "r"))
    if not pyproject["install"]["executable"]:
        return
    exec_fn = Path(sys.executable).parent / "Scripts" / f"{name}.bat"
    exec_content = f"py -m {name} %*"
    open(exec_fn, "w").write(exec_content)


def install(args):
    installcmd = ["pip", "install"]
    if args["dev"]:
        installcmd += ["-e"]
    installcmd += [args["src"]]
    return subprocess.call(installcmd)
