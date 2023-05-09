# pydev

[![Tests](https://github.com/mb-89/pydev/actions/workflows/tests.yml/badge.svg)](https://github.com/mb-89/pydev/actions/workflows/tests.yml)

A helper for developing python modules.
The idea of this tool is to provide similar features to rusts cargo and to put all
configuration needed for version control, testing, building, publishing etc into one tool (pydev)
and one config file (pyproject.toml).

A similar tool is poetry (https://python-poetry.org/docs/pyproject/#include-and-exclude),
however poetry didnt fit the niche that pydev occupies exactly.

The idea is as follows:
- Install pydev via pip install git+https://github.com/mb-89/pydev.git
- use pydev to install other modules via pydev install <...>. This will for example also set up pre-commit hooks.
- use commands like pydev prune,deps,test,build,release,... during development.