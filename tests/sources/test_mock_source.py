from typing import List

import pytest

from ablate.core.types import Run
from ablate.sources import Mock


@pytest.fixture
def mock_runs() -> List[Run]:
    source = Mock(
        grid={"model": ["resnet", "vgg"], "lr": [0.01, 0.001]},
        num_seeds=2,
        steps=10,
    )
    return source.load()


def test_mock_source_run_count(mock_runs: List[Run]) -> None:
    assert len(mock_runs) == 8


def test_mock_source_metrics_in_bounds(mock_runs: List[Run]) -> None:
    for run in mock_runs:
        metrics = run.metrics
        assert "accuracy" in metrics
        assert "f1" in metrics
        assert "loss" in metrics

        assert 0.0 <= metrics["accuracy"] <= 1.0
        assert 0.0 <= metrics["f1"] <= 1.0
        assert metrics["loss"] > 0.0


def test_mock_source_temporal_length(mock_runs: List[Run]) -> None:
    for run in mock_runs:
        for key in ["accuracy", "f1", "loss"]:
            assert key in run.temporal
            assert len(run.temporal[key]) == 10
