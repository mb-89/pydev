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
        return errno

    addExecutable(args)
    addGitPrecommitHook(args)
    return 0


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
    exec_content = "#!/bin/sh\npy -m pydev prune\nexit $?"
    if exec_fn.is_file():
        print(f"a pre-commit hook already exists @ {exec_fn}. Hook was not changed!")
        return
    open(exec_fn, "w").write(exec_content)


def addExecutable(args):
    f = Path(args["src"]) / "pyproject.toml"
    if not f.is_file():
        return
    pyproject = tomlkit.load(open(f, "r"))
    if not pyproject["install"]["executable"]:
        return
    exec_fn = Path(sys.executable).parent / "Scripts" / "pydev.bat"
    exec_content = "py -m pydev %*"
    open(exec_fn, "w").write(exec_content)


def install(args):
    installcmd = ["pip", "install"]
    postfix = ""
    if args["dev"]:
        installcmd += ["-e"]
        postfix = "[dev]"
    installcmd += [args["src"] + postfix]
    return subprocess.call(installcmd)
