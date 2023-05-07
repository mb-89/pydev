import subprocess

DESCRIPTION = "builds wheels and eggs from the given package"


def attachToArgparser(parser):
    parser.description = DESCRIPTION
    parser.add_argument("-s", "--src", type=str, default=".", help="source to build")


def main(args):
    return subprocess.call(f"py -m build {args['src']}")
