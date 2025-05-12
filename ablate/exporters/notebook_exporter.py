import sys
from typing import List

from matplotlib import pyplot as plt

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
from ablate.exporters.utils import HEADING_LEVELS
from ablate.report import Report

from .utils import create_metric_plot


def running_in_notebook() -> bool:
    return any("jupyter" in arg or "ipykernel" in arg for arg in sys.argv)


class Notebook(AbstractExporter):
    def __init__(self) -> None:
        super().__init__()
        try:
            from IPython.display import display  # noqa: F401
        except ImportError as e:
            raise ImportError(
                "Notebook exporter requires `jupyter`. "
                "Please install with `pip install ablate[jupyter]`."
            ) from e

    def export(self, report: Report) -> None:
        if not running_in_notebook():
            raise RuntimeError(
                "Notebook exporter can only be used inside a Jupyter notebook."
            )
        self.render_blocks(report)

    def render_text(self, block: AbstractTextBlock, runs: List[Run]) -> None:
        from IPython.display import Markdown, display

        if isinstance(block, Text):
            display(Markdown(block.build(runs)))
        elif isinstance(block, _Heading):
            level = HEADING_LEVELS[type(block)]
            display(Markdown(f"{'#' * level} {block.build(runs)}"))
        else:
            raise NotImplementedError(f"Unsupported text block: '{type(block)}'")

    def render_table(self, block: AbstractTableBlock, runs: List[Run]) -> None:
        from IPython.display import display

        display(block.build(runs))

    def render_figure(self, block: AbstractFigureBlock, runs: List[Run]) -> None:
        from IPython.display import Markdown, display

        if not isinstance(block, MetricPlot):
            raise NotImplementedError(f"Unsupported figure block: '{type(block)}'.")

        df = block.build(runs)
        if df.empty:
            m = f"*No data available for {', '.join(m.label for m in block.metrics)}*"
            display(Markdown(m))
            return

        fig = create_metric_plot(df, block.identifier.label)
        plt.close(fig)
        display(fig)
