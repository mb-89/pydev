"""Test module code using pytest."""

import os
import subprocess
from pathlib import Path


def attachToArgparser(parser):
    """Attach a subparser for this module to the given parser."""
    parser.description = globals()["__doc__"]
    parser.add_argument(
        "-s",
        "--src",
        type=str,
        default=".",
        help="source to test. the given folder should contain a src and test subfolder",
    )
    parser.add_argument("-show", action="store_true", help="pass to show the reports")
    parser.add_argument(
        "-f", "--filt", default="", type=str, help="regex that can be used to filter tests"
    )
    parser.add_argument("-d", "--deploy", action="store_true", help="pass to deploy to a tox venv")


def main(args):
    """Execute this modules function with the args defined in attachToArgparser."""
    rp = Path(args["src"]).resolve()
    print(f"testing {rp}")
    p = Path(args["src"])
    cmd = ["pytest", str(p), "-k", args["filt"]]
    reportpath = p / "tests" / "report"

    show = False
    if not args["filt"]:
        modname = rp.name
        covcmds = [f"--cov={modname}", "--cov-report=term-missing", "-v", "--cov-fail-under=100"]
        cmd.extend(covcmds)
        if args["show"]:
            reportcmds = [
                f"--cov-report=html:{reportpath}",
                f"--html={reportpath}/report.html",
                "--self-contained-html",
            ]
            cmd.extend(reportcmds)
            show = True
    errno = subprocess.call(cmd)

    if show:
        print("opening reports")
        r = p / "tests" / "report"
        os.system(str(r / "report.html"))
        os.system(str(r / "index.html"))

    if args["deploy"]:
        if errno:
            print("local tests failed, therefore deployed tests will be skipped.")
            return errno
        print("running tests deployed using tox...")
        errno = subprocess.call(["tox"], cwd=args["src"])

    return errno
