"""Helps developing python modules."""
try:  # pragma: no cover
    from pydev.cli import main
except ModuleNotFoundError:  # pragma: no cover
    # we need this so the vscode debugger works better
    from cli import main

import sys  # pragma: no cover

main(sys.argv[1:])  # pragma: no cover
