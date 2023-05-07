import subprocess

import pytest
import tomlkit

from pydev import cli


class MockRunResult:
    def __init__(self, stdout="") -> None:
        self.stdout = stdout.encode("cp1252")


def test_deps(monkeypatch, tmp_path):
    with monkeypatch.context() as mock:
        # no dev, success:
        mock.setattr(subprocess, "call", lambda x: 0)
        open(tmp_path / "requirements.txt", "w").write("bla>=1\n")
        tomlkit.dump({"dependencies": []}, open(tmp_path / "pyproject.toml", "w"))
        with pytest.raises(SystemExit) as exc:
            cli.main(["deps", "-s", str(tmp_path)])
        assert exc.value.code == 0
