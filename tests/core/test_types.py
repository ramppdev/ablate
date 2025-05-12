from pydantic import ValidationError
import pytest

from ablate.core.types import GroupedRun, Run


def test_run() -> None:
    run = Run(id="test_run", params={"param1": 1}, metrics={"metric1": 0.5})
    assert run.id == "test_run"
    assert run.params == {"param1": 1}
    assert run.metrics == {"metric1": 0.5}
    assert run.temporal == {}


def test_temporal_data() -> None:
    run = Run(
        id="test_run",
        params={"param1": 1},
        metrics={"metric1": 0.5},
        temporal={"metric1": [(0, 0.0), (1, 1.0), (2, 2.0)]},
    )
    assert run.temporal == {"metric1": [(0, 0.0), (1, 1.0), (2, 2.0)]}
    assert run.temporal["metric1"][0] == (0, 0.0)


def test_invalid_metrics_type() -> None:
    with pytest.raises(ValidationError):
        Run(id="bad", params={}, metrics="not a dict")  # type: ignore[arg-type]


def test_grouped_run() -> None:
    run1 = Run(id="run1", params={"param1": 1}, metrics={"metric1": 0.5})
    run2 = Run(id="run2", params={"param2": 2}, metrics={"metric2": 0.8})
    grouped_run = GroupedRun(key="group_key", value="group_value", runs=[run1, run2])
    assert grouped_run.key == "group_key"
    assert grouped_run.value == "group_value"
    assert len(grouped_run.runs) == 2
    assert grouped_run.runs[0].id == "run1"
    assert grouped_run.runs[1].id == "run2"


def test_invalid_runs_type() -> None:
    with pytest.raises(ValidationError):
        GroupedRun(key="group_key", value="group_value", runs=["not a run"])  # type: ignore[list-item]


def test_run_roundtrip_serialization() -> None:
    run = Run(
        id="run1",
        params={"x": 1},
        metrics={"acc": 0.9},
        temporal={"loss": [(0, 0.1), (1, 0.05)]},
    )
    data = run.model_dump()
    recovered = Run(**data)
    assert recovered == run
