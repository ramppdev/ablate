from pathlib import Path
import re
from typing import List

import matplotlib.pyplot as plt
import pytest

from ablate.blocks import H1, H2, MetricPlot, Table, Text
from ablate.core.types import Run
from ablate.exporters import Markdown
from ablate.queries import Metric, Param
from ablate.report import Report

from .utils import DummyFigureBlock, DummyTextBlock


class DummyBlock:
    pass


@pytest.fixture
def runs() -> list[Run]:
    return [
        Run(
            id="run1",
            params={"model": "resnet"},
            metrics={"accuracy": 0.8},
            temporal={"accuracy": [(0, 0.5), (1, 0.8)]},
        ),
        Run(
            id="run2",
            params={"model": "resnet"},
            metrics={"accuracy": 0.9},
            temporal={"accuracy": [(0, 0.6), (1, 0.9)]},
        ),
    ]


def test_export_text_blocks(tmp_path: Path, runs: List[Run]) -> None:
    report = Report(runs).add(H1("Heading 1"), Text("Some paragraph text."))
    out_path = tmp_path / "report.md"
    Markdown(output_path=str(out_path)).export(report)

    content = out_path.read_text()
    assert "# Heading 1" in content
    assert "Some paragraph text." in content


def test_export_table_block(tmp_path: Path, runs: List[Run]) -> None:
    table = Table(
        columns=[
            Param("model", label="Model"),
            Metric("accuracy", direction="max", label="Accuracy"),
        ]
    )
    report = Report(runs).add(table)
    out_path = tmp_path / "report.md"
    Markdown(output_path=str(out_path)).export(report)

    content = out_path.read_text().replace("\r\n", "\n")
    assert re.search(r"\|\s*Model\s*\|\s*Accuracy\s*\|", content)
    pattern = (
        r"\|\s*resnet\s*\|\s*0\.8\s*\|\s*\n"
        r"\|\s*resnet\s*\|\s*0\.9\s*\|"
    )
    assert re.search(pattern, content)


def test_export_figure_block(tmp_path: Path, runs: List[Run]) -> None:
    plot = MetricPlot(Metric("accuracy", direction="max"), identifier=Param("model"))
    report = Report(runs).add(plot)
    out_path = tmp_path / "report.md"
    exporter = Markdown(output_path=str(out_path))
    exporter.export(report)

    content = out_path.read_text()
    assert "![MetricPlot_" in content
    asset_path = tmp_path / ".ablate"
    assert asset_path.exists()
    files = list(asset_path.glob("MetricPlot_*.png"))
    assert len(files) == 1
    img = plt.imread(files[0])
    assert img.shape[-1] in {3, 4}


def test_export_figure_block_empty(tmp_path: Path) -> None:
    empty_run = Run(id="x", params={}, metrics={}, temporal={})
    plot = MetricPlot(Metric("accuracy", direction="max"), identifier=Param("model"))
    report = Report([empty_run]).add(plot)
    out_path = tmp_path / "report.md"
    Markdown(output_path=str(out_path)).export(report)

    content = out_path.read_text()
    assert "*No data available for accuracy*" in content


def test_unknown_block_raises(tmp_path: Path, runs: List[Run]) -> None:
    report = Report(runs)
    report += DummyBlock()  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="Unknown block type"):
        Markdown(output_path=str(tmp_path / "out.md")).export(report)


def test_unsupported_figure_block_raises(tmp_path: Path, runs: List[Run]) -> None:
    report = Report(runs).add(DummyFigureBlock())
    exporter = Markdown(output_path=str(tmp_path / "out.md"))
    with pytest.raises(NotImplementedError, match="Unsupported figure block"):
        exporter.export(report)


def test_unsupported_text_block_raises(tmp_path: Path, runs: List[Run]) -> None:
    report = Report(runs).add(DummyTextBlock("oops"))
    exporter = Markdown(output_path=str(tmp_path / "out.md"))
    with pytest.raises(NotImplementedError, match="Unsupported text block"):
        exporter.export(report)


def test_block_level_runs_override_global(tmp_path: Path, runs: List[Run]) -> None:
    scoped_runs = [runs[0]]
    report = Report(runs).add(
        Text("global"),
        Table([Param("model"), Metric("accuracy", "max")], runs=scoped_runs),
    )
    out_path = tmp_path / "report.md"
    Markdown(output_path=str(out_path)).export(report)
    content = out_path.read_text()
    assert "resnet" in content
    assert content.count("resnet") == 1


def test_export_heading_variants(tmp_path: Path, runs: List[Run]) -> None:
    report = Report(runs).add(H2("Section Title"))
    out_path = tmp_path / "headings.md"
    Markdown(output_path=str(out_path)).export(report)
    content = out_path.read_text()
    assert "## Section Title" in content


def test_export_table_block_with_csv(tmp_path: Path, runs: List[Run]) -> None:
    table = Table(
        columns=[Param("model"), Metric("accuracy", direction="max")],
    )
    report = Report(runs).add(table)
    out_path = tmp_path / "report.md"
    exporter = Markdown(output_path=str(out_path), export_csv=True)
    exporter.export(report)

    content = out_path.read_text()
    assert "resnet" in content
    asset_dir = tmp_path / ".ablate"
    csv_files = list(asset_dir.glob("Table_*.csv"))
    assert len(csv_files) == 1
    csv_content = csv_files[0].read_text()
    assert "model,accuracy" in csv_content
    assert "resnet,0.8" in csv_content


def test_export_figure_block_with_csv(tmp_path: Path, runs: List[Run]) -> None:
    plot = MetricPlot(Metric("accuracy", direction="max"), identifier=Param("model"))
    report = Report(runs).add(plot)
    out_path = tmp_path / "report.md"
    exporter = Markdown(output_path=str(out_path), export_csv=True)
    exporter.export(report)

    asset_dir = tmp_path / ".ablate"
    png_files = list(asset_dir.glob("MetricPlot_*.png"))
    assert len(png_files) == 1
    csv_files = list(asset_dir.glob("MetricPlot_*.csv"))
    assert len(csv_files) == 1
    csv_content = csv_files[0].read_text()
    assert "step,value,metric,run,run_id" in csv_content
    assert "0,0.5,accuracy,resnet,run1" in csv_content
    assert "1,0.9,accuracy,resnet,run2" in csv_content
