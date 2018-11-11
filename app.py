from pipenv_instance.core import PipenvInstance


def test_lock():
    with PipenvInstance() as p:
        with open(p.pipfile_path, "w") as f:
            contents = """
[packages]
requests-xml = "*"
            """.strip()
            f.write(contents)

        c = p.pipenv("lock")
        print(p.lockfile)


if __name__ == "__main__":
    test_lock()
