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
        (tmp_path / "src").mkdir()
        open(tmp_path / "src" / "requirements.txt", "w").write("bla>=1\n")
        dct = {"dependencies": [], "tool": {"tox": {"legacy_tox_ini": TOXSTUB}}}
        tomlkit.dump(dct, open(tmp_path / "pyproject.toml", "w"))
        with pytest.raises(SystemExit) as exc:
            cli.main(["deps", "-s", str(tmp_path)])
        assert exc.value.code == 0


TOXSTUB = """
[testenv]
deps =
    pytest
"""
