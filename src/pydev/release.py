"""Run all steps needed before we can safely push to remote."""
import subprocess
from pathlib import Path

import tomlkit


def attachToArgparser(parser):
    """Build the documentation for this package package."""
    parser.description = globals()["__doc__"]
    parser.add_argument("-s", "--src", type=str, default=".", help="source to install from")
    parser.add_argument(
        "-b",
        "--bump",
        type=str,
        default="none",
        help="which version to bump",
        choices=["none", "major", "minor", "patch", "dev"],
    )
    parser.add_argument(
        "-x",
        "--execute",
        action="store_true",
        help="pass to actually execute the release (push to remote)",
    )
    parser.add_argument(
        "-k",
        "--skip",
        action="store_true",
        help="pass to skip tests. Will ask for confirmation.",
    )


def main(args):
    """Execute this modules function with the args defined in attachToArgparser."""
    skip = False
    if args["skip"]:
        confirm = input("Are you sure you want to release without running checks? (y/[n])")
        if confirm != "y":
            return 1
        skip = True

    _, nv = bumpVersion(args)

    if not skip:
        errno = runprep(args)
        if errno:  # pragma: no cover: generic edgecase
            return errno

    if not args["execute"]:
        return 0
    else:
        return execute(args, nv)


def execute(args, nv):
    """Execute the final step of a release: push to the git remote."""
    mod = Path(args["src"]).resolve()
    cmd = ["git", "add", "-A"]
    errno = subprocess.call(cmd, cwd=mod)
    if errno:  # pragma: no cover:generic edgecase
        return errno

    msg = f"RELEASE {nv}"

    cmd = ["git", "commit", "-m", f"{msg}"]
    errno = subprocess.call(cmd, cwd=mod)
    if errno:  # pragma: no cover:generic edgecase
        return errno

    cmd = ["git", "tag", "-a", nv, "-m", f"{msg}"]
    errno = subprocess.call(cmd, cwd=mod)
    if errno:  # pragma: no cover:generic edgecase
        return errno

    return errno


def bumpVersion(args):
    """Bumps module version."""
    bump = args["bump"]
    mod = Path(args["src"]).resolve()
    meta = tomlkit.load(open(mod / "pyproject.toml", "r"))
    currver = meta["project"]["version"]
    if bump == "none":
        currver, currver

    # logic:
    # on mayor, bump major version, set rest to 0
    # on minor, bump minor version, set rest to 0
    # on patch, bump patch version, set rest to 0
    # on dev:
    # if no suffix, increase patch and add suffix:
    # if suffix present, increase suffix: alpha->beta->rc(x)
    if "-" not in currver:
        major, minor, patch = [int(x) for x in currver.split(".")]
        dev = ""
    else:
        pref, dev = currver.split("-")
        major, minor, patch = [int(x) for x in pref.split(".")]

    newver = currver
    if bump == "major":
        newver = f"{major+1}.0.0"
    elif bump == "minor":
        newver = f"{major}.{minor+1}.0"
    elif bump == "patch":
        newver = f"{major}.{minor}.{patch+1}"
    elif bump == "dev":
        if dev == "alpha":
            newver = f"{major}.{minor}.{patch}-beta"
        elif dev == "beta":
            newver = f"{major}.{minor}.{patch}-rc1"
        elif dev.startswith("rc"):
            try:
                no = int(dev[2:])
            except ValueError:
                no = 0
            newver = f"{major}.{minor}.{patch}-rc{no+1}"
        else:
            newver = f"{major}.{minor}.{patch+1}-alpha"
    else:
        return currver, currver

    meta["project"]["version"] = newver
    tomlkit.dump(meta, open(mod / "pyproject.toml", "w"))
    return currver, newver


def runprep(args):
    """Run all steps needed in preparation of a release."""
    mod = Path(args["src"]).resolve()
    cmd = ["py", "-m", "pydev", "install", "-s", f"{mod}", "-d"]
    errno = subprocess.call(cmd, cwd=mod)
    if errno:
        print(f"collecting deps returned <{errno}>.")
        return errno

    mod = Path(args["src"]).resolve()
    cmd = ["py", "-m", "pydev", "deps", "-s", f"{mod}"]
    errno = subprocess.call(cmd, cwd=mod)
    if errno:
        print(f"collecting deps returned <{errno}>.")
        return errno

    cmd = ["py", "-m", "pydev", "prune", "-s", f"{mod}"]
    errno = subprocess.call(cmd, cwd=mod)
    if errno:
        print(f"pruning returned <{errno}>.")
        return errno

    cmd = ["py", "-m", "pydev", "test", "-s", f"{mod}", "-d"]
    errno = subprocess.call(cmd, cwd=mod)
    if errno:
        print(f"testing returned <{errno}>.")
        return errno

    cmd = ["py", "-m", "pydev", "build", "-s", f"{mod}"]
    errno = subprocess.call(cmd, cwd=mod)
    if errno:
        print(f"building returned <{errno}>.")
        return errno

    cmd = ["py", "-m", "pydev", "doc", "-s", f"{mod}"]
    errno = subprocess.call(cmd, cwd=mod)
    if errno:
        print(f"building doc returned <{errno}>.")
        return errno
