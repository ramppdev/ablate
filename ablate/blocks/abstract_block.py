from abc import ABC, abstractmethod
from typing import Any, List

from ablate.core.types import Run


class AbstractBlock(ABC):
    def __init__(self, runs: List[Run] | None = None) -> None:
        """Abstract content block for a report.

        Args:
            runs: Optional list of runs to be used for the block instead of the default
                runs from the report. Defaults to None.
        """
        self.runs = runs

    @abstractmethod
    def build(self, runs: List[Run]) -> Any:
        """Build the intermediate representation of the block, ready for rendering
        and export.

        Args:
            runs: List of runs to be used for the block.

        Returns:
            The intermediate representation of the block.
        """
