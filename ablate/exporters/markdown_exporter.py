from pathlib import Path
from typing import List

from ablate.blocks import (
    AbstractFigureBlock,
    AbstractTableBlock,
    AbstractTextBlock,
    MetricPlot,
    Text,
)
from ablate.blocks.text_blocks import _Heading
from ablate.core.types import Run
from ablate.exporters.abstract_exporter import AbstractExporter
from ablate.report import Report

from .utils import HEADING_LEVELS, hash_dataframe, render_metric_plot


class Markdown(AbstractExporter):
    def __init__(
        self,
        output_path: str = "report.md",
        assets_dir: str | None = None,
        export_csv: bool = False,
    ) -> None:
        """Export the report as a markdown file.

        Args:
            output_path: The path to the output markdown file. Defaults to "report.md".
            assets_dir: The directory to store the assets (figures, etc.). If None,
                defaults to the parent directory of the output file with a ".ablate"
                subdirectory. Defaults to None.
            export_csv: Whether to export tables and plots as CSV files.
                Defaults to False.
        """
        self.output_path = Path(output_path)
        self.assets_dir = (
            Path(assets_dir) if assets_dir else self.output_path.parent / ".ablate"
        )
        self.assets_dir.mkdir(exist_ok=True)
        self.export_csv = export_csv

    def export(self, report: Report) -> None:
        content = self.render_blocks(report)
        with self.output_path.open("w", encoding="utf-8") as f:
            for block_output in content:
                f.write(block_output)
                f.write("\n\n")

    def render_text(self, block: AbstractTextBlock, runs: List[Run]) -> str:
        if isinstance(block, Text):
            return block.build(runs)
        if isinstance(block, _Heading):
            return f"{'#' * HEADING_LEVELS[type(block)]} {block.build(runs)}"
        raise NotImplementedError(f"Unsupported text block: '{type(block)}'.")

    def render_table(self, block: AbstractTableBlock, runs: List[Run]) -> str:
        df = block.build(runs)
        if self.export_csv:
            df.to_csv(
                self.assets_dir / f"{type(block).__name__}_{hash_dataframe(df)}.csv",
                index=False,
            )
        return df.to_markdown(index=False)

    def render_figure(self, block: AbstractFigureBlock, runs: List[Run]) -> str:
        if not isinstance(block, MetricPlot):
            raise NotImplementedError(f"Unsupported figure block: '{type(block)}'.")

        if self.export_csv:
            df = block.build(runs)
            df.to_csv(
                self.assets_dir / f"{type(block).__name__}_{hash_dataframe(df)}.csv",
                index=False,
            )

        filename = render_metric_plot(block, runs, self.assets_dir)
        if filename is None:
            return (
                f"*No data available for {', '.join(m.label for m in block.metrics)}*"
            )
        return f"![{filename}](.ablate/{filename})"
