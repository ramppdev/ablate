from typing import List

import pytest

from ablate.core.types import Run
from ablate.queries.query import Query
from ablate.queries.selectors import Metric, Param


@pytest.fixture
def runs() -> List[Run]:
    return [
        Run(id="a", params={"model": "resnet", "seed": 1}, metrics={"accuracy": 0.7}),
        Run(id="b", params={"model": "resnet", "seed": 2}, metrics={"accuracy": 0.8}),
        Run(id="c", params={"model": "vit", "seed": 1}, metrics={"accuracy": 0.9}),
    ]


def test_filter(runs: List[Run]) -> None:
    runs = Query(runs).filter(Param("model") == "resnet").all()
    assert len(runs) == 2
    assert all(r.params["model"] == "resnet" for r in runs)


def test_sort(runs: List[Run]) -> None:
    runs = Query(runs).sort(Metric("accuracy", direction="min")).all()
    assert [r.id for r in runs] == ["c", "b", "a"]


def test_head_tail(runs: List[Run]) -> None:
    q = Query(runs)
    assert q.head(1).all()[0].id == "a"
    assert q.tail(1).all()[0].id == "c"


def test_topk_bottomk(runs: List[Run]) -> None:
    q = Query(runs)
    top = q.topk(Metric("accuracy", direction="max"), k=2).all()
    bot = q.bottomk(Metric("accuracy", direction="max"), k=1).all()
    assert [r.id for r in top] == ["c", "b"]
    assert [r.id for r in bot] == ["a"]


def test_map(runs: List[Run]) -> None:
    q = Query(runs)

    def upper_case_id(run: Run) -> Run:
        run.id = run.id.upper()
        return run

    updated = q.map(upper_case_id).all()
    assert updated[0].id == "A"
    assert runs[0].id == "a"


def test_groupby_single_key(runs: List[Run]) -> None:
    gq = Query(runs).groupby(Param("model"))
    assert len(gq) == 2
    assert {g.value for g in gq._grouped} == {"resnet", "vit"}


def test_groupby_multiple_keys(runs: List[Run]) -> None:
    gq = Query(runs).groupby([Param("model"), Param("seed")])
    keys = {(g.key, g.value) for g in gq._grouped}
    assert len(keys) == 3


def test_groupdiff(runs: List[Run]) -> None:
    grouped = Query(runs).groupdiff(Param("seed"))._grouped
    expected_group_sizes = {"resnet": 2, "vit": 1}
    for group in grouped:
        model = group.runs[0].params["model"]
        assert len(group.runs) == expected_group_sizes[model]
    assert all(len(g.value) == 8 for g in grouped)


def test_query_copy_shallow(runs: List[Run]) -> None:
    original = Query(runs)
    copied = original.copy()

    assert copied._runs == original._runs
    assert copied._runs is not original._runs
    assert copied._runs[0] is original._runs[0]


def test_query_deepcopy(runs: List[Run]) -> None:
    original = Query(runs)
    deepcopied = original.deepcopy()
    assert deepcopied._runs == original._runs
    assert deepcopied._runs is not original._runs
    assert deepcopied._runs[0] is not original._runs[0]


def test_query_len(runs: List[Run]) -> None:
    assert len(Query(runs)) == 3


def test_project_reduces_parameter_space(runs: List[Run]) -> None:
    q = Query(runs).project(Param("model"))
    for run in q.all():
        assert set(run.params.keys()) == {"model"}
        assert set(run.metrics.keys()) == {"accuracy"}
