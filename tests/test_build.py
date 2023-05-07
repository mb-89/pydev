import subprocess

import pytest

from pydev import cli


def noop(*args, **kwargs):
    return 0


def test_build(monkeypatch):
    with monkeypatch.context() as mock:
        mock.setattr(subprocess, "call", noop)
        with pytest.raises(SystemExit) as exc:
            cli.main(["build", "-s", ".", "-show"])
        assert exc.value.code == 0
