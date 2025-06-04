from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from ablate.sources import TensorBoard


@patch.dict(
    "sys.modules",
    {"tensorboard.backend.event_processing.event_accumulator": None},
)
def test_import_error_if_tensorboard_not_installed() -> None:
    with pytest.raises(ImportError, match="TensorBoard source requires `tensorboard`"):
        TensorBoard(logdirs="/some/path")


@patch("tensorboard.backend.event_processing.event_accumulator.EventAccumulator")
def test_tensorboard_load_single_run(
    mock_event_accumulator: MagicMock, tmp_path: Path
) -> None:
    run_dir = tmp_path / "run1"
    run_dir.mkdir()
    (run_dir / "events.out.tfevents.12345").touch()

    mock_ea_instance = mock_event_accumulator.return_value
    mock_ea_instance.Tags.return_value = {"scalars": ["accuracy", "loss"]}
    mock_ea_instance.Scalars.side_effect = lambda tag: [
        SimpleNamespace(step=1, value=0.5 if tag == "accuracy" else 0.9)
    ]
    mock_ea_instance.Reload.return_value = None

    source = TensorBoard(logdirs=str(tmp_path))
    runs = source.load()

    assert len(runs) == 1
    run = runs[0]
    assert run.id == "run1"
    assert run.params == {}
    assert run.metrics == {"accuracy": 0.5, "loss": 0.9}
    assert run.temporal == {
        "accuracy": [(1, 0.5)],
        "loss": [(1, 0.9)],
    }


@patch("tensorboard.backend.event_processing.event_accumulator.EventAccumulator")
def test_tensorboard_load_multiple_runs(
    mock_event_accumulator: MagicMock, tmp_path: Path
) -> None:
    for name in ["runA", "runB"]:
        path = tmp_path / name
        path.mkdir()
        (path / "events.out.tfevents.12345").touch()

    mock_ea_instance = mock_event_accumulator.return_value
    mock_ea_instance.Tags.return_value = {"scalars": ["acc"]}
    mock_ea_instance.Scalars.return_value = [SimpleNamespace(step=1, value=0.75)]
    mock_ea_instance.Reload.return_value = None

    source = TensorBoard(logdirs=[str(tmp_path)])
    runs = source.load()

    run_ids = sorted(r.id for r in runs)
    assert run_ids == ["runA", "runB"]
    for run in runs:
        assert run.metrics["acc"] == 0.75
        assert run.temporal["acc"] == [(1, 0.75)]


@patch("tensorboard.backend.event_processing.event_accumulator.EventAccumulator")
def test_tensorboard_handles_empty_logs(
    mock_event_accumulator: MagicMock, tmp_path: Path
) -> None:
    logdir = tmp_path / "empty_run"
    logdir.mkdir()
    (logdir / "events.out.tfevents.12345").touch()

    mock_ea_instance = mock_event_accumulator.return_value
    mock_ea_instance.Tags.return_value = {"scalars": []}
    mock_ea_instance.Reload.return_value = None

    source = TensorBoard(logdirs=str(tmp_path))
    runs = source.load()

    assert len(runs) == 1
    assert runs[0].metrics == {}
    assert runs[0].temporal == {}
