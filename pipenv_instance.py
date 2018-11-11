import os
import warnings
from vistir.compat import ResourceWarning, fs_str
from vistir.path import mkdir_p
from tempfile import TemporaryDirectory
from pathlib import Path


class PipenvInstance:
    """An instance of a Pipenv Project..."""

    def __init__(self, pypi=None, pipfile=True, chdir=False, path=None, home_dir=None):
        self.pypi = pypi
        self.original_umask = os.umask(0o007)
        self.original_dir = os.path.abspath(os.curdir)
        os.environ["PIPENV_NOSPIN"] = fs_str("1")
        os.environ["CI"] = fs_str("1")
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.filterwarnings(
            "ignore", category=ResourceWarning, message="unclosed.*<ssl.SSLSocket.*>"
        )
        path = os.environ.get("PIPENV_PROJECT_DIR", None)
        if not path:
            self._path = TemporaryDirectory(suffix="-project", prefix="pipenv-")
            path = Path(self._path.name)
            try:
                self.path = str(path.resolve())
            except OSError:
                self.path = str(path.absolute())
        else:
            self._path = None
            self.path = path
        # set file creation perms
        self.pipfile_path = None
        self.chdir = chdir

        if self.pypi:
            os.environ["PIPENV_TEST_INDEX"] = fs_str("{0}/simple".format(self.pypi.url))

        if pipfile:
            p_path = os.sep.join([self.path, "Pipfile"])
            with open(p_path, "a"):
                os.utime(p_path, None)

            self.chdir = False or chdir
            self.pipfile_path = p_path

    def __enter__(self):
        os.environ["PIPENV_DONT_USE_PYENV"] = fs_str("1")
        os.environ["PIPENV_IGNORE_VIRTUALENVS"] = fs_str("1")
        os.environ["PIPENV_VENV_IN_PROJECT"] = fs_str("1")
        os.environ["PIPENV_NOSPIN"] = fs_str("1")
        if self.chdir:
            os.chdir(self.path)
        return self

    def __exit__(self, *args):
        warn_msg = "Failed to remove resource: {!r}"
        if self.chdir:
            os.chdir(self.original_dir)
        self.path = None
        if self._path:
            try:
                self._path.cleanup()
            except OSError as e:
                _warn_msg = warn_msg.format(e)
                warnings.warn(_warn_msg, ResourceWarning)
        os.umask(self.original_umask)

    def pipenv(self, cmd, block=True):
        if self.pipfile_path:
            os.environ["PIPENV_PIPFILE"] = fs_str(self.pipfile_path)
        # a bit of a hack to make sure the virtualenv is created

        with TemporaryDirectory(prefix="pipenv-", suffix="-cache") as tempdir:
            os.environ["PIPENV_CACHE_DIR"] = fs_str(tempdir.name)
            c = delegator.run("pipenv {0}".format(cmd), block=block)
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

    @property
    def pipfile(self):
        p_path = os.sep.join([self.path, "Pipfile"])
        with open(p_path, "r") as f:
            return toml.loads(f.read())

    @property
    def lockfile(self):
        p_path = self.lockfile_path
        with open(p_path, "r") as f:
            return json.loads(f.read())

    @property
    def lockfile_path(self):
        return os.sep.join([self.path, "Pipfile.lock"])

