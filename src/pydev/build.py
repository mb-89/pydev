"""Build wheels and eggs from the given package."""
import subprocess


def attachToArgparser(parser):
    """Attach a subparser for this module to the given parser."""
    parser.description = globals()["__doc__"]
    parser.add_argument("-s", "--src", type=str, default=".", help="source to build")


def main(args):
    """Execute this modules function with the args defined in attachToArgparser."""
    return subprocess.call(f"py -m build {args['src']}")
