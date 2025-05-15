from typing import List

import pandas as pd

from ablate.blocks import H1, MetricPlot, Table, Text
from ablate.core.types import Run
from ablate.queries.selectors import Metric, Param


def make_runs() -> List[Run]:
    return [
        Run(
            id="a",
            params={"model": "resnet", "seed": 1},
            metrics={"accuracy": 0.7},
            temporal={"accuracy": [(0, 0.6), (1, 0.7)]},
        ),
        Run(
            id="b",
            params={"model": "resnet", "seed": 2},
            metrics={"accuracy": 0.8},
            temporal={"accuracy": [(0, 0.7), (1, 0.8)]},
        ),
    ]


def test_text_blocks() -> None:
    assert Text(" simple ").build(make_runs()) == "simple"
    assert H1("# Title").build(make_runs()) == "# Title"


def test_table_block() -> None:
    table = Table(columns=[Param("model"), Param("seed")])
    df = table.build(make_runs())
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["model", "seed"]
    assert df.iloc[0]["model"] == "resnet"


def test_metric_plot_single() -> None:
    plot = MetricPlot(Metric("accuracy", direction="max"), identifier=Param("seed"))
    df = plot.build(make_runs())
    assert isinstance(df, pd.DataFrame)
    assert set(df.columns) >= {"step", "value", "metric", "run", "run_id"}
    assert df["metric"].unique().tolist() == ["accuracy"]


def test_metric_plot_multi() -> None:
    plot = MetricPlot([Metric("accuracy", direction="max")], identifier=Param("seed"))
    df = plot.build(make_runs())
    assert isinstance(df, pd.DataFrame)
    assert all(k in df.columns for k in ["step", "value", "metric", "run"])
