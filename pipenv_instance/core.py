import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, MutableMapping

import toml
import delegator

from delegator import Command

JSONTYPE = MutableMapping[str, Any]


class PipenvInstance:
    """An instance of a pipenv process"""

    def __init__(self) -> None:
        self._path = TemporaryDirectory(suffix="-project", prefix="pipenv-")
        self.path = Path(self._path.name)
        self.pipfile_path = self.path / "Pipfile"
        self.lockfile_path = self.path / "Pipfile.lock"

    def __enter__(self) -> "PipenvInstance":
        return self

    def __exit__(self, *args) -> None:
        self._path.cleanup()

    @property
    def pipfile(self) -> JSONTYPE:
        with open(str(self.pipfile_path.absolute()), "r") as f:
            return toml.loads(f.read())

    @property
    def lockfile(self) -> JSONTYPE:
        with open(str(self.lockfile_path.absolute()), "r") as f:
            return json.loads(f.read())

    def pipenv(self, cmd, block=True) -> Command:
        if self.pipfile_path:
            os.environ["PIPENV_PIPFILE"] = str(self.pipfile_path)
        # a bit of a hack to make sure the virtualenv is created

        with TemporaryDirectory(prefix="pipenv-", suffix="-cache") as tempdir:
            os.environ["PIPENV_CACHE_DIR"] = str(Path(tempdir).absolute())
            c = delegator.run(f"pipenv {cmd}", block=block)
            if "PIPENV_CACHE_DIR" in os.environ:
                del os.environ["PIPENV_CACHE_DIR"]

        if "PIPENV_PIPFILE" in os.environ:
            del os.environ["PIPENV_PIPFILE"]

        # Pretty output for failing tests.
        if block:
            print("$ pipenv {0}".format(cmd))
            print(c.out)
            print(c.err)
            if c.return_code != 0:
                print("Command failed...")

        # Where the action happens.
        return c
