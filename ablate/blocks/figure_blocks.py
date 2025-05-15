from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List

import pandas as pd

from ablate.queries import AbstractMetric, Id, Param

from .abstract_block import AbstractBlock


if TYPE_CHECKING:  # pragma: no cover
    from ablate.core.types import Run


class AbstractFigureBlock(AbstractBlock, ABC):
    @abstractmethod
    def build(self, runs: List[Run]) -> pd.DataFrame: ...


class MetricPlot(AbstractFigureBlock):
    def __init__(
        self,
        metrics: AbstractMetric | List[AbstractMetric],
        identifier: Param | None = None,
        runs: List[Run] | None = None,
    ) -> None:
        """Block for plotting metrics over time.

        Args:
            metrics: Metric or list of metrics to be plotted over time.
            identifier: Optional identifier for the runs. If None, the run ID is used.
                Defaults to None.
            runs: Optional list of runs to be used for the block instead of the default
                runs from the report. Defaults to None.
        """
        super().__init__(runs)
        self.metrics = metrics if isinstance(metrics, list) else [metrics]
        self.identifier = identifier or Id()

    def build(self, runs: List[Run]) -> pd.DataFrame:
        data = []
        for run in runs:
            for metric in self.metrics:
                series = run.temporal.get(metric.name, [])
                for step, value in series:
                    data.append(
                        {
                            "step": step,
                            "value": value,
                            "metric": metric.label,
                            "run": self.identifier(run),
                            "run_id": run.id,
                        }
                    )
        return pd.DataFrame(data)
