from abc import ABC, abstractmethod
from typing import List

from ablate.core.types import Run


class AbstractSource(ABC):
    @abstractmethod
    def load(self) -> List[Run]:
        """Load the data from the source.

        Returns:
            A list of runs with their parameters, metrics, and optionally temporal data.
        """
