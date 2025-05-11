from ablate.core.types import Run
from ablate.queries.query import Query
from ablate.queries.selectors import Metric, Param


def make_runs() -> list[Run]:
    return [
        Run(id="a", params={"model": "resnet", "seed": 1}, metrics={"accuracy": 0.7}),
        Run(id="b", params={"model": "resnet", "seed": 2}, metrics={"accuracy": 0.8}),
        Run(id="c", params={"model": "vit", "seed": 1}, metrics={"accuracy": 0.9}),
    ]


def test_filter() -> None:
    runs = Query(make_runs()).filter(Param("model") == "resnet").all()
    assert len(runs) == 2
    assert all(r.params["model"] == "resnet" for r in runs)


def test_sort() -> None:
    runs = Query(make_runs()).sort(Metric("accuracy", direction="min")).all()
    assert [r.id for r in runs] == ["c", "b", "a"]


def test_head_tail() -> None:
    q = Query(make_runs())
    assert q.head(1).all()[0].id == "a"
    assert q.tail(1).all()[0].id == "c"


def test_topk_bottomk() -> None:
    q = Query(make_runs())
    top = q.topk(Metric("accuracy", direction="max"), k=2).all()
    bot = q.bottomk(Metric("accuracy", direction="max"), k=1).all()
    assert [r.id for r in top] == ["c", "b"]
    assert [r.id for r in bot] == ["a"]


def test_map() -> None:
    q = Query(make_runs())

    def upper_case_id(run: Run) -> Run:
        run.id = run.id.upper()
        return run

    updated = q.map(upper_case_id).all()
    assert updated[0].id == "A"
    assert make_runs()[0].id == "a"


def test_groupby_single_key() -> None:
    gq = Query(make_runs()).groupby(Param("model"))
    assert len(gq) == 2
    assert {g.value for g in gq._grouped} == {"resnet", "vit"}


def test_groupby_multiple_keys() -> None:
    gq = Query(make_runs()).groupby([Param("model"), Param("seed")])
    keys = {(g.key, g.value) for g in gq._grouped}
    assert len(keys) == 3


def test_groupdiff() -> None:
    grouped = Query(make_runs()).groupdiff(Param("seed"))._grouped
    expected_group_sizes = {"resnet": 2, "vit": 1}
    for group in grouped:
        model = group.runs[0].params["model"]
        assert len(group.runs) == expected_group_sizes[model]
    assert all(len(g.value) == 8 for g in grouped)


def test_query_copy_shallow() -> None:
    original = Query(make_runs())
    copied = original.copy()

    assert copied._runs == original._runs
    assert copied._runs is not original._runs
    assert copied._runs[0] is original._runs[0]


def test_query_deepcopy() -> None:
    original = Query(make_runs())
    deepcopied = original.deepcopy()
    assert deepcopied._runs == original._runs
    assert deepcopied._runs is not original._runs
    assert deepcopied._runs[0] is not original._runs[0]


def test_query_len() -> None:
    assert len(Query(make_runs())) == 3
