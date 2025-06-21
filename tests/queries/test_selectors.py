import pytest

from ablate.core.types import Run
from ablate.queries.selectors import Id, Metric, Param, TemporalMetric


@pytest.fixture
def example_run() -> Run:
    return Run(
        id="run-42",
        params={"model": "resnet", "lr": 0.001},
        metrics={"accuracy": 0.91, "loss": 0.1},
        temporal={"accuracy": [(0, 0.5), (1, 0.8), (2, 0.9)]},
    )


def test_id_selector(example_run: Run) -> None:
    selector = Id()
    assert selector(example_run) == "run-42"
    assert selector(example_run) != "run-x"


def test_param_selector(example_run: Run) -> None:
    selector = Param("lr")
    assert selector(example_run) == 0.001
    assert (selector > 0.0001)(example_run)
    assert not (selector < 0.0001)(example_run)

    missing_selector = Param("missing")
    assert missing_selector(example_run) is None


def test_param_comparisons(example_run: Run) -> None:
    selector = Param("lr")
    assert (selector == 0.001)(example_run)
    assert not (selector == 0.01)(example_run)

    assert (selector != 0.01)(example_run)
    assert not (selector != 0.001)(example_run)

    assert (selector <= 0.001)(example_run)
    assert (selector >= 0.001)(example_run)
    assert not (selector <= 0.0001)(example_run)
    assert not (selector >= 0.01)(example_run)


def test_metric_selector(example_run: Run) -> None:
    selector = Metric("accuracy", direction="max")
    assert selector(example_run) == 0.91
    assert (selector > 0.5)(example_run)
    assert not (selector < 0.5)(example_run)

    missing = Metric("missing", direction="max")
    assert missing(example_run) == float("-inf")


def test_invalid_metric_direction() -> None:
    with pytest.raises(ValueError, match="Invalid direction"):
        Metric("accuracy", direction="invalid")  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("reduction", "expected"),
    [
        ("min", 0.5),
        ("max", 0.9),
        ("first", 0.5),
        ("last", 0.9),
    ],
)
def test_temporal_metric_selector(
    example_run: Run, reduction: str, expected: float
) -> None:
    selector = TemporalMetric("accuracy", direction="max", reduction=reduction)  # type: ignore[arg-type]
    assert selector(example_run) == expected


def test_temporal_metric_missing_returns_nan(example_run: Run) -> None:
    selector = TemporalMetric("not_logged", direction="max", reduction="max")
    assert selector(example_run) != selector(example_run)


def test_temporal_metric_invalid_reduction() -> None:
    with pytest.raises(ValueError, match="Invalid reduction method"):
        TemporalMetric("accuracy", direction="max", reduction="median")  # type: ignore[arg-type]


def test_predicate_and(example_run: Run) -> None:
    acc = Metric("accuracy", direction="max")
    loss = Metric("loss", direction="min")

    pred = (acc > 0.8) & (loss < 0.2)
    assert pred(example_run) is True

    pred = (acc > 0.95) & (loss < 0.2)
    assert pred(example_run) is False


def test_predicate_or(example_run: Run) -> None:
    acc = Metric("accuracy", direction="max")
    loss = Metric("loss", direction="min")

    pred = (acc > 0.95) | (loss < 0.2)
    assert pred(example_run) is True

    pred = (acc > 0.95) | (loss > 0.2)
    assert pred(example_run) is False


def test_predicate_not(example_run: Run) -> None:
    acc = Metric("accuracy", direction="max")

    pred = ~(acc > 0.95)
    assert pred(example_run) is True

    pred = ~(acc < 0.95)
    assert pred(example_run) is False


def test_chained_predicates(example_run: Run) -> None:
    acc = Metric("accuracy", direction="max")
    loss = Metric("loss", direction="min")
    lr = Param("lr")

    pred = ((acc > 0.8) & (loss < 0.2)) | (lr == 0.01)
    assert pred(example_run) is True

    pred = ((acc > 0.95) & (loss < 0.05)) | (lr == 0.02)
    assert pred(example_run) is False
