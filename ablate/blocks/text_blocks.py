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


class _Heading(AbstractTextBlock): ...


class H1(_Heading): ...


class H2(_Heading): ...


class H3(_Heading): ...


class H4(_Heading): ...


class H5(_Heading): ...


class H6(_Heading): ...


class Text(AbstractTextBlock): ...
