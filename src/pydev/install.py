"""Installs modules, including git hooks, debugger cfg, ..."""

import importlib.metadata as md
import json
import subprocess
import sys
from pathlib import Path

import tomlkit
from jsmin import jsmin


def attachToArgparser(parser):
    """Build the documentation for this package package."""
    parser.description = globals()["__doc__"]
    parser.add_argument("-d", "--dev", action="store_true", help="installs in dev mode")
    parser.add_argument("-s", "--src", type=str, default=".", help="source to install from")


def main(args):
    """Execute this modules function with the args defined in attachToArgparser."""
    errno = install(args)
    if errno:
        return errno

    addExecutable(args)
    addGitPrecommitHook(args)
    addVSCodeConfig(args)
    addGithubAction(args)
    return 0


def addGithubAction(args):
    """Add useful github actions."""
    if not args["dev"]:
        return
    dst = Path(args["src"]) / ".github" / "workflows" / "tests.yml"
    if not dst.is_file():
        dst.parent.mkdir(parents=True, exist_ok=True)
    metadata = md.metadata(__name__.split(".")[0])
    open(dst, "w").write(
        TESTYML.replace("#VERSION#", metadata["Requires-Python"].replace(">=", ""))
    )


def addVSCodeConfig(args):
    """Add a debug config to .vscode folder that helps with test debugging."""
    if not args["dev"]:
        return
    dst = Path(args["src"]) / ".vscode" / "launch.json"
    if not dst.is_file():
        dst.parent.mkdir(parents=True, exist_ok=True)
        cfg = {"configurations": [DEBUGCFG]}
        json.dump(cfg, open(dst, "w"))
    cfg = json.loads(jsmin(open(dst, "r").read()))
    name = "Python: Debug Test"
    existingcfg = [x for x in cfg["configurations"] if x["name"] == name]
    if existingcfg:  # dont override an existing cfg
        print(f"since a {name} cfg already exists @ {dst}, it was not overwritten!")
        return
    cfg["configurations"].append(DEBUGCFG)
    json.dump(cfg, open(dst, "w"), indent=4)


def addGitPrecommitHook(args):
    """Add the prune command to the pre-commit hooks of the git repo."""
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
    exec_content = PRECOMMIT
    if exec_fn.is_file():
        print(f"a pre-commit hook already exists @ {exec_fn}. Hook was not changed!")
        return
    open(exec_fn, "w").write(exec_content)


def addExecutable(args):
    """Add an executable to the python script folder, if enabled in pyproject.toml."""
    f = Path(args["src"]) / "pyproject.toml"
    if not f.is_file():
        return
    pyproject = tomlkit.load(open(f, "r"))
    if not pyproject["install"]["executable"]:
        return
    pname = pyproject["project"]["name"]
    exec_fn = Path(sys.executable).parent / "Scripts" / f"{pname}.bat"
    exec_content = f"py -m {pname} %*"
    open(exec_fn, "w").write(exec_content)


def install(args):
    """Install the given source and make some useful modifications to the install."""
    installcmd = ["pip", "install"]
    postfix = ""
    if args["dev"]:
        installcmd += ["-e"]
        postfix = "[dev]"
    installcmd += [args["src"] + postfix]
    return subprocess.call(installcmd)


PRECOMMIT = """#!/bin/sh
py -m pydev prune
exit $?
"""

DEBUGCFG = {
    "name": "Python: Debug Test",
    "type": "python",
    "request": "launch",
    "program": "${file}",
    "purpose": ["debug-test"],
    "console": "integratedTerminal",
    "env": {"PYTEST_ADDOPTS": "--capture=sys --no-cov -s"},
}

TESTYML = """
name: Tests

on:
  - push
  - pull_request

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [windows-latest]
        python-version: ['#VERSION#']

    steps:
    - uses: actions/checkout@v2
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run:
        python -m pip install --upgrade pip
        pip install tox tox-gh-actions
    - name: Test with tox
      run: tox
"""
