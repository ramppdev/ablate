import tomli

import ablate


def test_version() -> None:
    with open("pyproject.toml", "rb") as f:
        pyproject = tomli.load(f)
    assert pyproject["project"]["version"] == ablate.__version__
