from typing import List
from unittest.mock import patch

import matplotlib.pyplot as plt
import pandas as pd
import pytest

from ablate import Report
from ablate.blocks import H2, MetricPlot, Table, Text
from ablate.core.types import Run
from ablate.exporters.notebook_exporter import Notebook, running_in_notebook
from ablate.queries import Metric, Param

from .utils import DummyFigureBlock, DummyTextBlock


@pytest.fixture
def runs() -> List[Run]:
    return [
        Run(
            id="r1",
            params={"model": "resnet"},
            metrics={"acc": 0.8},
            temporal={"acc": [(0, 0.5), (1, 0.8)]},
        ),
        Run(
            id="r2",
            params={"model": "resnet"},
            metrics={"acc": 0.9},
            temporal={"acc": [(0, 0.6), (1, 0.9)]},
        ),
    ]


def test_render_text_block(runs: List[Run]) -> None:
    block = Text("Hello *world*")
    with patch("IPython.display.display") as mock_display:
        Notebook().render_text(block, runs)
        assert mock_display.call_count == 1
        assert "Hello" in mock_display.call_args[0][0].data


def test_render_heading_block(runs: List[Run]) -> None:
    block = H2("Section")
    with patch("IPython.display.display") as mock_display:
        Notebook().render_text(block, runs)
        assert mock_display.call_count == 1
        assert mock_display.call_args[0][0].data.startswith("##")


def test_render_table_block(runs: List[Run]) -> None:
    table = Table(columns=[Param("model"), Metric("acc", direction="max")])
    with patch("IPython.display.display") as mock_display:
        Notebook().render_table(table, runs)
        df = mock_display.call_args[0][0]
        assert isinstance(df, pd.DataFrame)
        assert "model" in df.columns
        assert len(df) == 2


def test_render_metric_plot(runs: List[Run]) -> None:
    plot = MetricPlot(Metric("acc", direction="max"), identifier=Param("model"))
    with patch("IPython.display.display") as mock_display:
        Notebook().render_figure(plot, runs)
        fig = mock_display.call_args[0][0]
        assert isinstance(fig, plt.Figure)


def test_render_empty_plot() -> None:
    empty_run = Run(id="x", params={}, metrics={}, temporal={})
    plot = MetricPlot(Metric("acc", direction="max"), identifier=Param("model"))
    with patch("IPython.display.display") as mock_display:
        Notebook().render_figure(plot, [empty_run])
        text = mock_display.call_args[0][0]
        assert "*No data available for acc*" in text.data


def test_running_in_notebook_true(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.argv", ["ipykernel_launcher"])
    assert running_in_notebook() is True


def test_running_in_notebook_false(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.argv", ["some_script.py"])
    assert running_in_notebook() is False


def test_notebook_import_error() -> None:
    with (
        patch.dict("sys.modules", {"IPython.display": None}),
        pytest.raises(ImportError, match="requires `jupyter`"),
    ):
        Notebook()


def test_export_runs(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.argv", ["ipykernel_launcher"])
    report = Report([])
    with patch.object(Notebook, "render_blocks", return_value=[]) as mock_render:
        Notebook().export(report)
        mock_render.assert_called_once_with(report)


def test_export_outside_notebook(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.argv", ["script.py"])

    with pytest.raises(RuntimeError, match="only be used inside a Jupyter notebook"):
        Notebook().export(Report([]))


def test_render_text_not_implemented(runs: List[Run]) -> None:
    dummy = DummyTextBlock("oops")
    with pytest.raises(NotImplementedError):
        Notebook().render_text(dummy, runs)


def test_render_figure_not_implemented(runs: List[Run]) -> None:
    dummy = DummyFigureBlock()
    with pytest.raises(NotImplementedError):
        Notebook().render_figure(dummy, runs)
