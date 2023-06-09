import subprocess

import pytest

from pydev import cli


def noop(*args, **kwargs):
    return 0


def test_prune(monkeypatch):
    with monkeypatch.context() as mock:
        mock.setattr(subprocess, "call", noop)
        with pytest.raises(SystemExit) as exc:
            cli.main(["prune", "-s", "."])
        assert exc.value.code == 0
