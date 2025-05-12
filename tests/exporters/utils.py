from typing import List

from ablate.blocks import AbstractFigureBlock, AbstractTextBlock
from ablate.core.types import Run


class DummyTextBlock(AbstractTextBlock):
    def build(self, runs: List[Run]) -> str:  # type: ignore[override]
        return "not supported"


class DummyFigureBlock(AbstractFigureBlock):
    def build(self, runs: List[Run]) -> str:  # type: ignore[override]
        return "not a dataframe"
