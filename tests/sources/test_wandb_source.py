from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from ablate.sources import WandB


@patch("wandb.Api")
def test_wandb_loads_metrics_and_temporal_data(mock_api_class: MagicMock) -> None:
    mock_api = mock_api_class.return_value
    mock_run = MagicMock()
    mock_run.id = "run-123"
    mock_run.config = {"lr": 0.01, "batch_size": 32}
    mock_run.summary = {"accuracy": 0.92, "loss": 0.1}

    mock_history_df = pd.DataFrame(
        {
            "_step": [1, 2],
            "accuracy": [0.89, 0.92],
        }
    )
    mock_run.history.return_value = mock_history_df
    mock_api.runs.return_value = [mock_run]

    source = WandB(project="my-project", entity="my-entity")
    runs = source.load()

    assert len(runs) == 1
    r = runs[0]
    assert r.id == "run-123"
    assert r.params == {"lr": 0.01, "batch_size": 32}
    assert r.metrics == {"accuracy": 0.92, "loss": 0.1}
    assert r.temporal == {"accuracy": [(1, 0.89), (2, 0.92)]}


@patch("wandb.Api")
def test_wandb_ignores_missing_history_keys(mock_api_class: MagicMock) -> None:
    mock_api = mock_api_class.return_value
    mock_run = MagicMock()
    mock_run.id = "run-xyz"
    mock_run.config = {}
    mock_run.summary = {"metric_logged": 0.5}

    mock_run.history.return_value = pd.DataFrame(
        {
            "_step": [1, 2],
            "some_other_metric": [0.3, 0.4],
        }
    )

    mock_api.runs.return_value = [mock_run]

    source = WandB(project="dummy", entity="dummy")
    runs = source.load()

    r = runs[0]
    assert r.metrics == {"metric_logged": 0.5}
    assert r.temporal == {}


@patch.dict("sys.modules", {"wandb": None})
def test_import_error_if_wandb_not_installed() -> None:
    with pytest.raises(ImportError, match="Wandb source requires `wandb`"):
        WandB(project="dummy")
