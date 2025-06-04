from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd
import pytest
import yaml

from ablate.sources import Autrainer
from ablate.sources.autrainer_source import flatten_autrainer_config


if TYPE_CHECKING:
    from ablate.core.types import Run


def write_yaml(path: Path, content: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(content))


def write_csv(path: Path, content: dict) -> None:
    df = pd.DataFrame(content)
    df.to_csv(path, index=False)


def make_dummy_run(path: Path) -> None:
    write_yaml(
        path / ".hydra" / "config.yaml",
        {
            "model": {
                "id": "MyModel",
                "hidden": 128,
                "nested": {"id": "Submodule", "layers": 2},
            },
            "optimizer": {"lr": 0.01},
        },
    )
    write_yaml(
        path / "_best" / "dev.yaml",
        {"accuracy": {"all": 0.85}, "loss": {"all": 0.3}, "iteration": 5},
    )
    write_yaml(
        path / "_test" / "test_holistic.yaml",
        {"accuracy": {"all": 0.8}, "loss": {"all": 0.35}, "iteration": 5},
    )
    write_csv(
        path / "metrics.csv",
        {
            "iteration": [1, 2, 3],
            "accuracy": [0.7, 0.75, 0.8],
            "loss": [0.4, 0.38, 0.36],
        },
    )


def test_raises_if_experiment_missing(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="No autrainer experiment found"):
        Autrainer(results_dir=str(tmp_path), experiment_id="no_such_id")


def test_loads_single_run_correctly(tmp_path: Path) -> None:
    exp_id = "exp-001"
    run_path = tmp_path / exp_id / "training" / "run0"
    make_dummy_run(run_path)

    source = Autrainer(results_dir=str(tmp_path), experiment_id=exp_id)
    runs = source.load()

    assert len(runs) == 1
    r: Run = runs[0]
    assert r.id == "run0"

    # Flattened params
    assert r.params["model"] == "MyModel"
    assert r.params["model.nested"] == "Submodule"
    assert r.params["model.hidden"] == 128
    assert r.params["model.nested.layers"] == 2
    assert r.params["optimizer.lr"] == 0.01

    # Merged dev/test metrics
    assert r.metrics == {
        "accuracy": 0.85,
        "loss": 0.3,
        "test_accuracy": 0.8,
        "test_loss": 0.35,
    }

    # Temporal metrics
    assert r.temporal == {
        "accuracy": [(1, 0.7), (2, 0.75), (3, 0.8)],
        "loss": [(1, 0.4), (2, 0.38), (3, 0.36)],
    }


def test_skips_non_directories(tmp_path: Path) -> None:
    exp_id = "exp-002"
    base = tmp_path / exp_id / "training"
    run_dir = base / "run_dir"
    run_file = base / "README.txt"

    make_dummy_run(run_dir)
    run_file.write_text("This is not a run directory")

    source = Autrainer(results_dir=str(tmp_path), experiment_id=exp_id)
    runs = source.load()

    assert len(runs) == 1
    assert runs[0].id == "run_dir"


def test_flatten_config_yields_id_only_dict() -> None:
    config = {"id": "only"}
    result = dict(flatten_autrainer_config(config))
    assert result == {"": "only"}


def test_flatten_config_with_list_of_dicts() -> None:
    config = [
        {"id": "first"},
        {"name": "second", "id": "second_id"},
    ]
    result = dict(flatten_autrainer_config(config))

    assert result == {"0": "first", "1": "second_id", "1.name": "second"}
