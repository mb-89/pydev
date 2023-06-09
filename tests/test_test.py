import os
import subprocess
from pathlib import Path

import pytest

from pydev import cli


def noop(*args, **kwargs):
    return 0


def noop_nonzero(*args, **kwargs):
    return 1


def test_test(monkeypatch):
    with monkeypatch.context() as mock:
        mock.setattr(subprocess, "call", noop)
        mock.setattr(os, "system", noop)

        lp = Path(".") / "tests" / ".log"
        if lp.is_file():
            lp.unlink()

        with pytest.raises(SystemExit) as exc:
            cli.main(["test", "-s", ".", "-d"])
        assert exc.value.code == 0

        mock.setattr(subprocess, "call", noop_nonzero)
        with pytest.raises(SystemExit) as exc:
            cli.main(["test", "-s", ".", "-show", "-d"])
        assert exc.value.code == 1
