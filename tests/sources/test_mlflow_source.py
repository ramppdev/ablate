from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from ablate.sources import MLflow


@pytest.mark.filterwarnings("ignore::pydantic.PydanticDeprecatedSince20")
@pytest.mark.parametrize(
    ("tracking_uri", "expected_uri_startswith"),
    [
        (None, None),
        ("/some/local/path", "file://"),
        ("http://mlflow.mycompany.com", "http://"),
        ("https://mlflow.mycompany.com", "https://"),
        ("file:///already/uri", "file://"),
    ],
)
@patch("mlflow.tracking.MlflowClient")
def test_mlflow_uri_resolution(
    client: MagicMock,
    tracking_uri: str,
    expected_uri_startswith: str,
) -> None:
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

    source = MLflow(tracking_uri=tracking_uri, experiment_names="default")
    runs = source.load()

    if expected_uri_startswith is None:
        client.assert_called_once_with()
    else:
        uri_arg = client.call_args.args[0]
        assert uri_arg.startswith(expected_uri_startswith)

    r = runs[0]
    assert r.id == "run-1"
    assert r.params == {"lr": "0.01", "mlflow.runName": "example"}
    assert r.metrics == {"accuracy": 0.9}
    assert r.temporal == {"accuracy": [(1, 0.9)]}


@patch.dict("sys.modules", {"mlflow.tracking": None})
def test_import_error_if_mlflow_not_installed() -> None:
    with pytest.raises(ImportError, match="MLflow source requires `mlflow`"):
        MLflow(tracking_uri="/fake", experiment_names=["exp"])


@patch("mlflow.tracking.MlflowClient")
def test_mlflow_raises_on_invalid_experiment_name(client: MagicMock) -> None:
    mock_client = client.return_value
    mock_client.get_experiment_by_name.return_value = None

    source = MLflow(tracking_uri="/fake/path", experiment_names=["nonexistent"])

    with pytest.raises(ValueError, match="One or more experiment names not found"):
        source.load()
