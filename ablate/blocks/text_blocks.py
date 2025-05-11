from abc import ABC
from typing import List

from ablate.core.types import Run

from .abstract_block import AbstractBlock


class AbstractTextBlock(AbstractBlock, ABC):
    def __init__(self, text: str, runs: List[Run] | None = None) -> None:
        """Block containing styled text for a report.

        Args:
            text: The text content of the block.
            runs: Optional list of runs to be used for the block instead of the default
                runs from the report. Defaults to None.
        """
        super().__init__(runs)
        self.text = text

    def build(self, runs: List[Run]) -> str:
        return self.text.strip()


class H1(AbstractTextBlock): ...


class H2(AbstractTextBlock): ...


class H3(AbstractTextBlock): ...


class H4(AbstractTextBlock): ...


class H5(AbstractTextBlock): ...


class H6(AbstractTextBlock): ...


class Text(AbstractTextBlock): ...
