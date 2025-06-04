from unittest.mock import MagicMock, patch

import pytest

from ablate.sources import ClearML


@patch("clearml.Task.get_task")
@patch("clearml.Task.query_tasks")
def test_clearml_loads_metrics_and_temporal_data(
    mock_query_tasks: MagicMock,
    mock_get_task: MagicMock,
) -> None:
    mock_query_tasks.return_value = ["clearml-001"]

    mock_task = MagicMock()
    mock_task.id = "clearml-001"
    mock_task.get_parameters.return_value = {"lr": 0.001, "epochs": 10}
    mock_task.get_reported_scalars.return_value = {
        "title": {
            "accuracy": {"x": [1, 2], "y": [0.85, 0.9]},
            "loss": {"x": [1, 2], "y": [0.25, 0.2]},
        }
    }

    mock_get_task.return_value = mock_task

    source = ClearML(project_name="example")
    runs = source.load()

    assert len(runs) == 1
    r = runs[0]
    assert r.id == "clearml-001"
    assert r.params == {"lr": 0.001, "epochs": 10}
    assert r.metrics == {"accuracy": 0.9, "loss": 0.2}
    assert r.temporal == {
        "accuracy": [(1, 0.85), (2, 0.9)],
        "loss": [(1, 0.25), (2, 0.2)],
    }


@patch.dict("sys.modules", {"clearml": None})
def test_import_error_if_clearml_not_installed() -> None:
    with pytest.raises(ImportError, match="ClearML source requires `clearml`"):
        ClearML(project_name="fail")
