import json
import subprocess
import sys

import pytest
import tomlkit

from pydev import cli


class MockRunResult:
    def __init__(self, stdout="") -> None:
        self.stdout = stdout.encode("cp1252")


def test_install_nodev(monkeypatch, tmp_path):
    with monkeypatch.context() as mock:
        # no dev, success:
        mock.setattr(subprocess, "call", lambda x: 0)
        mock.setattr(sys, "executable", str(tmp_path / "Scripts"))
        (tmp_path / "Scripts").mkdir()
        with pytest.raises(SystemExit) as exc:
            cli.main(["install", "-s", "."])
        assert exc.value.code == 0


def test_install_dev(monkeypatch, tmp_path):
    with monkeypatch.context() as mock:
        mock.setattr(sys, "executable", str(tmp_path / "Scripts"))

        def f1(*args, **kwargs):
            return MockRunResult("")

        def f2(*args, **kwargs):
            return MockRunResult(str(tmp_path / "DOESNTEXIST"))

        def f3(*args, **kwargs):
            return MockRunResult(str(tmp_path))

        mock.setattr(subprocess, "run", f1)

        # dev, fail:
        mock.setattr(subprocess, "call", lambda x: 1)
        with pytest.raises(SystemExit) as exc:
            cli.main(["install", "-s", ".", "-d"])
        assert exc.value.code == 1

        # dev, invalid dir:
        mock.setattr(subprocess, "call", lambda x: 0)
        with pytest.raises(SystemExit) as exc:
            cli.main(["install", "-s", str(tmp_path), "-d"])
        assert exc.value.code == 0

        # dev, with and without executable
        (tmp_path / "Scripts").mkdir()

        tomlkit.dump(
            {"install": {"executable": True}, "project": {"name": "test"}},
            open(tmp_path / "pyproject.toml", "w"),
        )
        with pytest.raises(SystemExit) as exc:
            cli.main(["install", "-s", str(tmp_path), "-d"])
        assert exc.value.code == 0

        jsoncfg = tmp_path / ".vscode" / "launch.json"
        jsoncfg.unlink()  # remove debug cfg
        open(jsoncfg, "w").write(json.dumps({"configurations": []}))

        tomlkit.dump({"install": {"executable": False}}, open(tmp_path / "pyproject.toml", "w"))
        with pytest.raises(SystemExit) as exc:
            cli.main(["install", "-s", str(tmp_path), "-d"])
        assert exc.value.code == 0

        # special cases for the pre-commit hook:
        with pytest.raises(SystemExit) as exc:
            cli.main(["install", "-s", str(tmp_path), "-d"])
        assert exc.value.code == 0
        mock.setattr(subprocess, "run", f2)
        with pytest.raises(SystemExit) as exc:
            cli.main(["install", "-s", str(tmp_path), "-d"])
        assert exc.value.code == 0

        mock.setattr(subprocess, "run", f3)
        hook = tmp_path / ".git" / "hooks" / "pre-commit"
        hook.parent.mkdir(parents=True)
        # this will create the hook:
        with pytest.raises(SystemExit) as exc:
            cli.main(["install", "-s", str(tmp_path), "-d"])
        assert exc.value.code == 0
        # this will skip the hook, since its already there:
        with pytest.raises(SystemExit) as exc:
            cli.main(["install", "-s", str(tmp_path), "-d"])
        assert exc.value.code == 0
