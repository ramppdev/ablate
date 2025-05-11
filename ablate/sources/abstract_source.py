from abc import ABC, abstractmethod
from typing import List

from ablate.core.types import Run


class AbstractSource(ABC):
    @abstractmethod
    def load(self) -> List[Run]: ...
