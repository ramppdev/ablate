from typing import List

import pytest

from ablate.core.types import GroupedRun, Run
from ablate.queries.grouped_query import GroupedQuery
from ablate.queries.query import Query
from ablate.queries.selectors import Metric, Param


@pytest.fixture
def runs() -> List[Run]:
    return [
        Run(id="a", params={"model": "resnet", "seed": 1}, metrics={"accuracy": 0.7}),
        Run(id="b", params={"model": "resnet", "seed": 2}, metrics={"accuracy": 0.8}),
        Run(id="c", params={"model": "vit", "seed": 1}, metrics={"accuracy": 0.6}),
        Run(id="d", params={"model": "vit", "seed": 2}, metrics={"accuracy": 0.9}),
    ]


@pytest.fixture
def grouped(runs: List[Run]) -> GroupedQuery:
    return Query(runs).groupby(Param("model"))


def test_filter_keeps_matching_groups(grouped: GroupedQuery) -> None:
    filtered = grouped.filter(lambda g: g.value == "resnet")
    assert len(filtered) == 1
    assert all(run.params["model"] == "resnet" for run in filtered.all())


def test_map_modifies_each_group(grouped: GroupedQuery) -> None:
    def fn(group: GroupedRun) -> GroupedRun:
        group.runs = [Run(**{**r.model_dump(), "id": r.id + "_x"}) for r in group.runs]
        return group

    mapped = grouped.map(fn)
    assert all(r.id.endswith("_x") for r in mapped.all())


def test_sort_sorts_within_each_group(grouped: GroupedQuery) -> None:
    grouped = grouped.sort(Metric("accuracy", direction="max"), ascending=True)
    for group in grouped._grouped:
        accs = [r.metrics["accuracy"] for r in group.runs]
        assert accs == sorted(accs)


def test_head_tail_topk_bottomk_all_return_expected_shape(
    grouped: GroupedQuery,
) -> None:
    assert len(grouped.head(1).all()) == 2
    assert len(grouped.tail(1).all()) == 2
    assert len(grouped.topk(Metric("accuracy", direction="max"), 1).all()) == 2
    assert len(grouped.bottomk(Metric("accuracy", direction="max"), 1).all()) == 2


def test_aggregate_all_strategies(grouped: GroupedQuery) -> None:
    m = Metric("accuracy", direction="max")
    assert len(grouped.aggregate("first", over=m).all()) == 2
    assert len(grouped.aggregate("last", over=m).all()) == 2
    assert len(grouped.aggregate("best", over=m).all()) == 2
    assert len(grouped.aggregate("worst", over=m).all()) == 2
    assert len(grouped.aggregate("mean", over=m).all()) == 2

    with pytest.raises(ValueError, match="Unsupported aggregation method"):
        grouped.aggregate("unsupported", over=m)  # type: ignore[arg-type]


def test_aggregate_best_worst_missing_over(grouped: GroupedQuery) -> None:
    with pytest.raises(ValueError, match="Method 'best' requires a metric"):
        grouped.aggregate("best")
    with pytest.raises(ValueError, match="Method 'worst' requires a metric"):
        grouped.aggregate("worst")


def test_aggregate_mean_collapses_metadata_and_temporal() -> None:
    run1 = Run(
        id="a",
        params={"model": "resnet", "seed": 1},
        metrics={"acc": 0.8},
        temporal={"acc": [(1, 0.2), (2, 0.6)]},
    )
    run2 = Run(
        id="b",
        params={"model": "resnet", "seed": 2},
        metrics={"acc": 0.4},
        temporal={"acc": [(1, 0.6), (2, 1.0)]},
    )
    grouped = GroupedQuery([GroupedRun(key="model", value="resnet", runs=[run1, run2])])
    agg = grouped.aggregate("mean", over=Metric("acc", direction="max")).all()[0]

    assert agg.params["model"] == "resnet"
    assert agg.params["seed"] == "#"
    assert agg.metrics["acc"] == pytest.approx(0.6)
    assert agg.temporal["acc"] == [(1, 0.4), (2, 0.8)]


def test_to_query_and_all_return_same_runs(grouped: GroupedQuery) -> None:
    assert grouped._to_query().all() == grouped.all()


def test_copy_and_deepcopy(grouped: GroupedQuery) -> None:
    shallow = grouped.copy()
    deep = grouped.deepcopy()

    assert shallow._grouped == grouped._grouped
    assert shallow._grouped is not grouped._grouped

    assert deep._grouped == grouped._grouped
    assert deep._grouped is not grouped._grouped
    assert all(
        dr is not gr for dr, gr in zip(deep._grouped, grouped._grouped, strict=False)
    )


def test_grouped_query_project_reduces_param_space(grouped: GroupedQuery) -> None:
    grouped = grouped.project(Param("model"))
    for group in grouped._grouped:
        for run in group.runs:
            assert set(run.params.keys()) == {"model"}
            assert set(run.metrics.keys()) == {"accuracy"}
