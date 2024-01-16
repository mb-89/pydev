import os
import shutil
import subprocess

import pytest
import tomlkit

from pydev import cli


def noop(*args, **kwargs):
    return 0


def test_doc(monkeypatch, tmp_path):
    f = tmp_path / "doc" / "conf.py"
    f.parent.mkdir()
    open(f, "w").write("test\nversion = '0.0.0'\nrelease = '0.0.0'\n")
    dct = {"project": {"name": "test", "authors": [{"name": "test"}], "version": "0.0.0"}}
    tomlkit.dump(dct, open(tmp_path / "pyproject.toml", "w"))
    f2 = tmp_path / "doc" / "index.rst"
    open(f2, "w").write("test")
    with monkeypatch.context() as mock:
        mock.setattr(subprocess, "call", noop)
        mock.setattr(os, "system", noop)
        mock.setattr(shutil, "rmtree", noop)
        with pytest.raises(SystemExit) as exc:
            cli.main(["doc", "-s", str(tmp_path)])
        assert exc.value.code == 0
