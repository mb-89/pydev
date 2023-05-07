import argparse
import importlib.metadata as md
import importlib.util
import re
import sys
from pathlib import Path


def main(argv):
    metadata = md.metadata(__name__.split(".")[0])
    modname = metadata["Name"]
    parser = argparse.ArgumentParser(
        prog=modname,
        description=metadata["Summary"],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-v", "--version", action="store_true", help="prints version")

    subparsers = parser.add_subparsers(dest="subparser_name")
    submodules = list(collectsubmodules(modname))
    submodDict = {}

    for x in submodules:
        k = x.__name__.split(".")[-1]
        v = (x, subparsers.add_parser(k, help=x.DESCRIPTION))
        x.attachToArgparser(v[1])
        submodDict[k] = v

    kwargs = vars(parser.parse_args(argv))

    if kwargs["version"]:
        print(metadata["version"])
        return 0
    if not argv:
        parser.print_help()
        return 0

    for k, v in submodDict.items():
        if kwargs.get("subparser_name") == k:
            mod = v[0]
            parser = v[1]
            subargv = [x for x in argv if x != k]
            kwargs = vars(parser.parse_args(subargv))
            sys.exit(mod.main(kwargs))


def collectsubmodules(parent):
    f = Path(__file__)
    for x in f.parent.glob("*.py"):
        if x.name.startswith("_") or x.name == f.name:
            continue
        mainExists = re.findall(r"^def main\((.*)\):(.*)$", open(x, "r").read(), re.MULTILINE)
        if not mainExists:  # pragma: no cover (since in a clean directory, we wont have this)
            continue
        modname = f"{parent}.{x.stem}"
        spec = importlib.util.spec_from_file_location(modname, x)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[modname] = mod
        spec.loader.exec_module(mod)
        yield mod
