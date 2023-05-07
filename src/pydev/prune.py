import subprocess
from pathlib import Path

LINELEN = 100
DESCRIPTION = "prunes code, including black, isort, flake8, ..."


def attachToArgparser(parser):
    parser.description = DESCRIPTION
    parser.add_argument(
        "-s",
        "--src",
        type=str,
        default=".",
        help="source to prune. the given folder should contain a src subfolder",
    )


def main(args):
    print(f"pruning {Path(args['src']).resolve()}")
    print("Formatting via black:")
    subprocess.call(["black", args["src"], "--line-length", f"{LINELEN}"])
    print("sorting imports:")
    subprocess.call(["isort", args["src"]])
    print("Linting via flake8:")
    flakeignore = [
        "E203",  # See https://github.com/PyCQA/pycodestyle/issues/373
    ]
    flake_ret = subprocess.call(
        [
            "flake8",
            args["src"],
            f"--extend-ignore={''.join(flakeignore)}",
            f"--max-line-length={LINELEN}",  # fits together with black
        ]
    )
    return flake_ret
