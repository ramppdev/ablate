from abc import ABC, abstractmethod
from typing import List

import pandas as pd

from ablate.core.types import Run
from ablate.queries import AbstractSelector

from .abstract_block import AbstractBlock


class AbstractTableBlock(AbstractBlock, ABC):
    def __init__(
        self,
        columns: List[AbstractSelector],
        runs: List[Run] | None = None,
    ) -> None:
        """Table block for a report.

        Args:
            columns: Columns to be included in the table. Each column is defined by a
                selector that extracts the data from the runs.
            runs: Optional list of runs to be used for the block instead of the default
                runs from the report. Defaults to None.
        """
        super().__init__(runs)
        self.columns = columns

    @abstractmethod
    def build(self, runs: List[Run]) -> pd.DataFrame: ...


class Table(AbstractTableBlock):
    def build(self, runs: List[Run]) -> pd.DataFrame:
        rows = []
        for run in runs:
            row = {}
            for column in self.columns:
                row[column.label] = column(run)
            rows.append(row)
        return pd.DataFrame(rows, columns=[column.label for column in self.columns])
