from __future__ import annotations

from typing import TYPE_CHECKING, List

from typing_extensions import Self


if TYPE_CHECKING:  # pragma: no cover
    from ablate.blocks import AbstractBlock
    from ablate.core.types import Run


class Report:
    def __init__(self, runs: List[Run]) -> None:
        """Report mapping a list of runs to a list of blocks.

        Args:
            runs: List of runs to be associated with the report.
        """
        self.runs = runs
        self.blocks: List[AbstractBlock] = []

    def add(self, *blocks: AbstractBlock) -> Self:
        """Add one or more blocks to the report.

        Args:
            blocks: One or more blocks to be added to the report.

        Returns:
            The updated report with the added blocks.
        """
        for block in blocks:
            self.blocks.append(block)
        return self

    def __iadd__(self, block: AbstractBlock) -> Self:
        self.blocks.append(block)
        return self

    def __add__(self, block: AbstractBlock) -> Report:
        r = Report(self.runs)
        r.blocks = self.blocks + [block]
        return r
