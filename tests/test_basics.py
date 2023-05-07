import pytest

from pydev import cli


def test_cli():
    assert cli.main([]) == 0
    assert cli.main(["-v"]) == 0

    for cmd in ["deps", "install", "prune", "test"]:
        with pytest.raises(SystemExit) as exc:
            cli.main([cmd, "-h"])
        assert exc.value.code == 0
