"""Prunes code, including black, isort, flake8, ..."""

import subprocess
from pathlib import Path

LINELEN = 100


def attachToArgparser(parser):
    """Build the documentation for this package package."""
    parser.description = globals()["__doc__"]
    parser.add_argument(
        "-s",
        "--src",
        type=str,
        default=".",
        help="source to prune. the given folder should contain a src subfolder",
    )


def main(args):
    """Execute this modules function with the args defined in attachToArgparser."""
    print(f"pruning {Path(args['src']).resolve()}")
    print("Formatting via black:")
    subprocess.call(["black", args["src"], "--line-length", f"{LINELEN}"])
    print("sorting imports:")
    subprocess.call(["isort", args["src"]])
    print("Linting via flake8:")
    flakeignore = [
        "E203",  # See https://github.com/PyCQA/pycodestyle/issues/373
        "D107",
        "D105",
        "F405",
        "F403",
        "D107",  # we dont need docstrings for __init__
    ]
    flake_ret = subprocess.call(
        [
            "flake8",
            args["src"],
            f"--extend-ignore={','.join(flakeignore)}",
            f"--max-line-length={LINELEN}",  # fits together with black
            "--exclude=doc/,.tox/",
            # no docstrings needed for tests:
            f"--per-file-ignores={args['src']}/tests/*:D103,D100,D101",
        ]
    )
    return flake_ret
