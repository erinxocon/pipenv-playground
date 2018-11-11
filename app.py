from pipenv_instance.core import PipenvInstance


def test_lock():
    with PipenvInstance() as p:
        with open(p.pipfile_path, "w") as f:
            contents = """
[[source]]
url = "https://pypi.org/simple"
verify_ssl = true
name = "pypi"

[packages]
responder = "*"
delegator-py = "*"
toml = "*"

[dev-packages]
mypy = "*"
black = "*"

[requires]
python_version = "3.6"

[pipenv]
allow_prereleases = true
            """.strip()
            f.write(contents)

        c = p.pipenv("lock")
        print(p.lockfile)


if __name__ == "__main__":
    test_lock()
