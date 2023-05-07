import importlib.metadata as md
import os
import subprocess
from pathlib import Path


def attachToArgparser(parser):
    parser.description = "routines for testing python code."
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


def main(args):
    print(f"testing {Path(args['src']).resolve()}")
    p = Path(args["src"])
    cmd = ["pytest", str(p), "-k", args["filt"]]
    show = False
    if not args["filt"]:
        metadata = md.metadata(__name__.split(".")[0])
        modname = metadata["Name"]
        covcmds = [f"--cov={modname}", "--cov-report=term-missing", "-v", "--cov-fail-under=100"]
        cmd.extend(covcmds)
        if args["show"]:
            reportcmds = [
                "--cov-report=html:tests/report",
                "--html=tests/report/report.html",
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
    return errno
