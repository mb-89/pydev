import builtins
import subprocess

import pytest

from pydev import cli
from pydev.release import bumpVersion


def noop(*args, **kwargs):
    return 0


def checkretcode(fn, retcode):
    with pytest.raises(SystemExit) as exc:
        fn()
    assert exc.value.code == retcode


def test_versionbumping(tmp_path):
    open(tmp_path / "pyproject.toml", "w").write('[project]\nversion="0.0.0"')

    assert bumpVersion({"src": str(tmp_path), "bump": "major"})[-1] == "1.0.0"
    assert bumpVersion({"src": str(tmp_path), "bump": "minor"})[-1] == "1.1.0"
    assert bumpVersion({"src": str(tmp_path), "bump": "patch"})[-1] == "1.1.1"
    assert bumpVersion({"src": str(tmp_path), "bump": "dev"})[-1] == "1.1.2-alpha"
    assert bumpVersion({"src": str(tmp_path), "bump": "dev"})[-1] == "1.1.2-beta"
    assert bumpVersion({"src": str(tmp_path), "bump": "dev"})[-1] == "1.1.2-rc1"
    assert bumpVersion({"src": str(tmp_path), "bump": "dev"})[-1] == "1.1.2-rc2"

    open(tmp_path / "pyproject.toml", "w").write('[project]\nversion="0.0.0-bla"')
    assert bumpVersion({"src": str(tmp_path), "bump": "dev"})[-1] == "0.0.1-alpha"
    open(tmp_path / "pyproject.toml", "w").write('[project]\nversion="0.0.0-rcx"')
    assert bumpVersion({"src": str(tmp_path), "bump": "dev"})[-1] == "0.0.0-rc1"


callMock_failon = ""


def callMock(*args, **kwargs):
    errno = 1 if callMock_failon in args[0] else 0
    return errno


def test_release(monkeypatch):
    global callMock_failon

    with monkeypatch.context() as mock:
        mock.setattr(subprocess, "call", noop)
        checkretcode(lambda: cli.main(["release"]), 0)
        mock.setattr(builtins, "input", lambda x: "y")
        checkretcode(lambda: cli.main(["release", "-k"]), 0)
        mock.setattr(builtins, "input", lambda x: "n")
        checkretcode(lambda: cli.main(["release", "-k"]), 1)

        mock.setattr(subprocess, "call", callMock)
        checkretcode(lambda: cli.main(["release", "-x"]), 0)
        callMock_failon = "doc"
        checkretcode(lambda: cli.main(["release", "-x"]), 1)
        callMock_failon = "build"
        checkretcode(lambda: cli.main(["release", "-x"]), 1)
        callMock_failon = "test"
        checkretcode(lambda: cli.main(["release", "-x"]), 1)
        callMock_failon = "prune"
        checkretcode(lambda: cli.main(["release", "-x"]), 1)
        callMock_failon = "deps"
        checkretcode(lambda: cli.main(["release", "-x"]), 1)
        callMock_failon = "install"
        checkretcode(lambda: cli.main(["release", "-x"]), 1)
