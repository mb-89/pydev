import subprocess
import sys

import pytest

from pydev import cli


def noop(*args, **kwargs):
    return 0


def test_init(monkeypatch, tmp_path):
    with monkeypatch.context() as mock:
        mock.setattr(subprocess, "call", noop)
        mock.setattr(sys, "executable", str(tmp_path / "Scripts"))
        (tmp_path / "Scripts").mkdir()
        with pytest.raises(SystemExit) as exc:
            cli.main(["init", "dummy", "mb", "-f", "-d", f"{tmp_path}", "-r", "bla"])
        assert exc.value.code == 0

        # run again to make sure we trigger a fault
        with pytest.raises(SystemExit) as exc:
            cli.main(["init", "dummy", "mb", "-d", f"{tmp_path}"])
        assert exc.value.code == 1
