from types import SimpleNamespace
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest

from ablate.sources import MLflow


if TYPE_CHECKING:
    from ablate.core.types import Run


@pytest.mark.filterwarnings("ignore::pydantic.PydanticDeprecatedSince20")
@patch("mlflow.tracking.MlflowClient")
def test_load_converts_mlflow_runs_to_runs(client: MagicMock) -> None:
    mock_client = client.return_value
    mock_run = SimpleNamespace(
        info=SimpleNamespace(run_id="run-1"),
        data=SimpleNamespace(
            params={"lr": "0.01"},
            metrics={"accuracy": 0.9},
            tags={"mlflow.runName": "example"},
        ),
    )

    mock_client.get_experiment_by_name.return_value = SimpleNamespace(
        experiment_id="123"
    )
    mock_client.search_runs.return_value = [mock_run]
    mock_client.get_metric_history.return_value = [SimpleNamespace(step=1, value=0.9)]

    source = MLflow(tracking_uri="/fake/path", experiment_names=["default"])
    runs = source.load()
    r: Run = runs[0]

    assert len(runs) == 1
    assert r.id == "run-1"
    assert r.params == {"lr": "0.01", "mlflow.runName": "example"}
    assert r.metrics == {"accuracy": 0.9}
    assert r.temporal == {"accuracy": [(1, 0.9)]}


def test_import_error_if_mlflow_not_installed() -> None:
    with (
        patch.dict("sys.modules", {"mlflow.tracking": None}),
        pytest.raises(ImportError, match="MLflow source requires `mlflow`"),
    ):
        MLflow(tracking_uri="/fake", experiment_names=["exp"])
