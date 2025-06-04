from abc import ABC, abstractmethod
from typing import Any, Callable, List, cast

from ablate.blocks import (
    AbstractBlock,
    AbstractFigureBlock,
    AbstractTableBlock,
    AbstractTextBlock,
)
from ablate.core.types import Run
from ablate.report import Report


class AbstractExporter(ABC):
    @abstractmethod
    def export(self, report: Report) -> None:
        """Export the report.

        Should call :meth:`~ablate.exporters.AbstractExporter.render_blocks` to generate
        the content of the report.

        Args:
            report: The report to be exported.
        """

    def render_blocks(self, report: Report) -> List[Any]:
        """Render a blocks of the report.

        Args:
            report: The report to be rendered.

        Raises:
            ValueError: If the block type is not supported.

        Returns:
            List of rendered blocks.
        """
        render_map = {
            AbstractTextBlock: self.render_text,
            AbstractTableBlock: self.render_table,
            AbstractFigureBlock: self.render_figure,
        }
        content = []
        for block in report.blocks:
            for block_type, render_fn in render_map.items():
                if isinstance(block, block_type):
                    fn = cast("Callable[[AbstractBlock, List[Run]], Any]", render_fn)
                    content.append(self._apply_render_fn(block, fn, report.runs))
                    break
            else:
                raise ValueError(f"Unknown block type: '{type(block)}'.")
        return content

    @staticmethod
    def _apply_render_fn(
        block: AbstractBlock,
        fn: Callable[[AbstractBlock, List[Run]], Any],
        runs: List[Run],
    ) -> Any:
        if block.runs:
            return fn(block, block.runs)
        return fn(block, runs)

    @abstractmethod
    def render_text(self, block: AbstractTextBlock, runs: List[Run]) -> Any:
        """Render a text block.

        Args:
            block: The text block to be rendered.
            runs: The list of runs to be used for the block.

        Returns:
            The rendered text block.
        """

    @abstractmethod
    def render_table(self, block: AbstractTableBlock, runs: List[Run]) -> Any:
        """Render a table block.

        Args:
            block: The table block to be rendered.
            runs: The list of runs to be used for the block.

        Returns:
            The rendered table block.
        """

    @abstractmethod
    def render_figure(self, block: AbstractFigureBlock, runs: List[Run]) -> Any:
        """Render a figure block.

        Args:
            block: The figure block to be rendered.
            runs: The list of runs to be used for the block.

        Returns:
            The rendered figure block.
        """
