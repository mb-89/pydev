"""Initialize a new repo, using pydev as a template."""
import shutil
import subprocess
from pathlib import Path

import tomlkit


def attachToArgparser(parser):
    """Attach a subparser for this module to the given parser."""
    parser.description = globals()["__doc__"]
    parser.add_argument("name", help="repo name")
    parser.add_argument("author", help="repo author")

    parser.add_argument("-r", "--remote", help="remote url for git", default="")
    parser.add_argument(
        "-f", "--force", help="pass to overwrite existing dirs", action="store_true"
    )
    parser.add_argument("-d", "--dst", help="destination folder", default=Path("."), type=Path)


def main(args):
    """Execute this modules function with the args defined in attachToArgparser."""
    modname = args["name"]
    dst = args["dst"] / modname
    if args["force"]:
        shutil.rmtree(dst, ignore_errors=True)
    try:
        dst.mkdir(parents=True)
    except FileExistsError:
        print(f"{dst} already exists. Aborted init.")
        exit(1)
    print(f"created {dst}.")

    # create empty readme
    readme = ["# " + modname]

    if args["remote"]:
        rem = args["remote"]
        ymlpath = "/actions/workflows/tests.yml/badge.svg"
        readme.append(f"\n[![Tests]({rem}{ymlpath})]({rem}{ymlpath})")

    readme.append("\nDoes nothing (yet).")
    open(dst / "README.md", "w").write("\n".join(readme))

    # create pyproject.toml with changes (use "Do/Does nothing yet" for docstring and descr)
    # we dont need to fix the dependencies here. they will be fixed by calling deps later.
    pypsrc = Path(__file__).parent.parent.parent / "pyproject.toml"
    pypdst = dst / "pyproject.toml"
    pyproject = tomlkit.load(open(pypsrc, "r"))
    pyproject["project"]["name"] = modname
    pyproject["project"]["version"] = "0.0.0"
    pyproject["project"]["description"] = "Does nothing (yet)."
    pyproject["project"]["authors"] = [{"name": args["author"]}]
    tomlkit.dump(pyproject, open(pypdst, "w"))

    # copy gitignore
    shutil.copyfile(pypsrc.parent / ".gitignore", dst / ".gitignore")
    # create a test that only checks the version feature
    dsttest = dst / "tests" / "test_basics.py"
    dsttest.parent.mkdir(parents=True)
    open(dsttest, "w").write(TEST.replace("#MOD", modname))

    # create a src folder that only contains main, init and cli
    src = dst / "src" / modname
    src.mkdir(parents=True)

    open(src / "cli.py", "w").write(CLI.replace("#MOD", modname))
    open(src / "__init__.py", "w").write('''"""Do nothing (yet)."""''')
    open(src / "__main__.py", "w").write(
        MAIN.replace("#MOD", modname).replace("#DESC", "Do nothing (yet).")
    )

    # run pydev deps
    cmd = ["py", "-m", "pydev", "deps", "-s", f"{str(dst)}"]
    subprocess.call(cmd)

    # run pydev install
    cmd = ["py", "-m", "pydev", "install", "-s", f"{str(dst)}", "-d"]
    subprocess.call(cmd)

    # initialize git
    cmd = ["git", "init"]
    subprocess.call(cmd, cwd=dst)
    if args["remote"]:
        cmd = ["git", "remote", "add", args["remote"]]
    subprocess.call(cmd, cwd=dst)

    # run pydev release (bump version to 0.0.1 alpha, prune, test, doc)
    # this yields a cli that only contains -h and -v
    return 0


TEST = """from #MOD import cli

def test_cli():
    assert cli.main(["-v"]) == 0
"""

CLI = '''
"""Provide a cli for all #MOD submodules."""

import argparse
import importlib.metadata as md

def main(argv):
    """Parse args and call requested functions"""
    metadata = md.metadata(__name__.split(".")[0])
    modname = metadata["Name"]
    parser = argparse.ArgumentParser(
        prog=modname,
        description=metadata["Summary"],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-v", "--version", action="store_true", help="prints version")
    kwargs = vars(parser.parse_args(argv))

    if kwargs["version"]:
        print(metadata["version"])
        return 0
'''

MAIN = '''"""#DESC"""
try:  # pragma: no cover
    from #MOD.cli import main
except ModuleNotFoundError:  # pragma: no cover
    # we need this so the vscode debugger works better
    from cli import main

import sys  # pragma: no cover

main(sys.argv[1:])  # pragma: no cover

'''
