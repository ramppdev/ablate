from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from typing import TYPE_CHECKING, Callable, Dict, List, Literal, Union

from ablate.core.types import GroupedRun, Run


if TYPE_CHECKING:  # pragma: no cover
    from .query import Query  # noqa: TC004
    from .selectors import AbstractMetric, AbstractParam


class GroupedQuery:
    def __init__(self, groups: List[GroupedRun]) -> None:
        """Query interface for manipulating grouped runs in a functional way.

        All methods operate on a shallow copy of the runs in the query, so the original
        runs are not modified and assumed to be immutable.

        Args:
            groups: A list of grouped runs to be queried.
        """
        self._grouped = groups

    def filter(self, fn: Callable[[GroupedRun], bool]) -> GroupedQuery:
        """Filter the grouped runs in the grouped query based on a predicate function.

        Args:
            fn: Predicate function that takes in a grouped run and returns a boolean
                value.

        Returns:
            A new grouped query with the grouped runs that satisfy the predicate
            function.
        """
        return GroupedQuery([g for g in self._grouped[:] if fn(g)])

    def map(self, fn: Callable[[GroupedRun], GroupedRun]) -> GroupedQuery:
        """Apply a function to each grouped run in the grouped query.

        This function is intended to be used for modifying the grouped runs in the
        grouped query. The function should return a new grouped run object as the
        original grouped run is not modified.

        Args:
            fn: Function that takes in a grouped run and returns a new grouped run
                object.

        Returns:
            A new grouped query with the modified grouped runs.
        """
        return GroupedQuery([fn(deepcopy(g)) for g in self._grouped])

    def sort(self, key: AbstractMetric, ascending: bool = False) -> GroupedQuery:
        """Sort the runs inside each grouped run in the grouped query based on a metric.

        Args:
            key: Metric to sort the grouped runs by.
            ascending: Whether to sort in ascending order.
                Defaults to False (descending order).

        Returns:
            A new grouped query with the grouped runs sorted by the specified metric.
        """
        return GroupedQuery(
            [
                GroupedRun(
                    key=g.key,
                    value=g.value,
                    runs=sorted(g.runs, key=key, reverse=not ascending),
                )
                for g in self._grouped
            ]
        )

    def project(
        self, selectors: Union[AbstractParam, List[AbstractParam]]
    ) -> GroupedQuery:
        """Project the parameter space of the grouped runs in the grouped query to a
        subset of parameters only including the specified selectors.

        This function is intended to be used for reducing the dimensionality of the
        parameter space and therefore operates on a deep copy of the grouped runs in the
        grouped query.

        Args:
            selectors: Selector or list of selectors to project the grouped runs by.

        Returns:
            A new grouped query with the projected grouped runs.
        """
        if not isinstance(selectors, list):
            selectors = [selectors]

        names = {s.name for s in selectors}
        projected: List[GroupedRun] = []

        for group in deepcopy(self._grouped):
            for run in group.runs:
                run.params = {k: v for k, v in run.params.items() if k in names}
            projected.append(group)

        return GroupedQuery(projected)

    def head(self, n: int) -> Query:
        """Get the first n runs inside each grouped run.

        Args:
            n: Number of runs to return per group.

        Returns:
            A new query with the first n runs from each grouped run.
        """
        return GroupedQuery(
            [
                GroupedRun(key=g.key, value=g.value, runs=g.runs[:n])
                for g in self._grouped
            ]
        )._to_query()

    def tail(self, n: int) -> Query:
        """Get the last n runs inside each grouped run.

        Args:
            n: Number of runs to return per group.

        Returns:
            A new query with the last n runs from each grouped run.
        """
        return GroupedQuery(
            [
                GroupedRun(key=g.key, value=g.value, runs=g.runs[-n:])
                for g in self._grouped
            ]
        )._to_query()

    def topk(self, metric: AbstractMetric, k: int) -> Query:
        """Get the top k runs inside each grouped run based on a metric.

        Args:
            metric: Metric to sort the runs by.
            k: Number of top runs to return per group.

        Returns:
            A new query with the top k runs from each grouped run based on the
            specified metric.
        """
        return GroupedQuery(
            [
                GroupedRun(
                    key=g.key,
                    value=g.value,
                    runs=sorted(g.runs, key=metric, reverse=metric.direction == "min")[
                        :k
                    ],
                )
                for g in self._grouped
            ]
        )._to_query()

    def bottomk(self, metric: AbstractMetric, k: int) -> Query:
        """Get the bottom k runs inside each grouped run based on a metric.

        Args:
            metric: Metric to sort the runs by.
            k: Number of bottom runs to return per group.

        Returns:
            A new query with the bottom k runs from each grouped run based on the
            specified metric.
        """
        return GroupedQuery(
            [
                GroupedRun(
                    key=g.key,
                    value=g.value,
                    runs=sorted(g.runs, key=metric, reverse=metric.direction == "max")[
                        :k
                    ],
                )
                for g in self._grouped
            ]
        )._to_query()

    def aggregate(
        self,
        method: Literal["first", "last", "best", "worst", "mean"],
        over: AbstractMetric | None = None,
    ) -> Query:
        """Aggregate each group of runs using a specified method.

        Supported methods include:
          * :attr:`"first"`: Selects the first run from each group.
          * :attr:`"last"`: Selects the last run from each group.
          * :attr:`"best"`: Selects the run with the best value based on the given
            metric.
          * :attr:`"worst"`: Selects the run with the worst value based on the given
            metric.
          * :attr:`"mean"`: Computes the mean run across all runs in each group,
            including averaged metrics and temporal data, and collapsed metadata.

        Args:
            method: Aggregation strategy to apply per group.
            over: The metric used for comparison when using "best" or "worst" methods.
                Has no effect for "first", "last", or "mean" methods.
                Defaults to None.

        Raises:
            ValueError: If an unsupported aggregation method is provided or if the
                "best" or "worst" method is used without a specified metric.


        Returns:
            A new query with the aggregated runs from each group.
        """
        if method in {"best", "worst"} and over is None:
            raise ValueError(
                f"Method '{method}' requires a metric to be specified for comparison."
            )
        from .query import Query

        match method:
            case "first":
                return self.head(1)
            case "last":
                return self.tail(1)
            case "best":
                assert over is not None
                return self.topk(over, 1)
            case "worst":
                assert over is not None
                return self.bottomk(over, 1)
            case "mean":
                return Query([self._mean_run(g) for g in self._grouped])
            case _:
                raise ValueError(
                    f"Unsupported aggregation method: '{method}'. Must be "
                    "'first', 'last', 'best', 'worst', or 'mean'."
                )

    @staticmethod
    def _mean_run(group: GroupedRun) -> Run:
        def _mean(values: List[float]) -> float:
            return sum(values) / len(values) if values else float("nan")

        def _mean_temporal(runs: List[Run]) -> Dict[str, List[tuple[int, float]]]:
            all_keys = set().union(*(r.temporal.keys() for r in runs))
            step_accumulator: Dict[str, Dict[int, List[float]]] = {}

            for key in all_keys:
                step_values = defaultdict(list)
                for run in runs:
                    for step, val in run.temporal.get(key, []):
                        step_values[step].append(val)
                step_accumulator[key] = step_values

            return {
                key: sorted(
                    (step, sum(vals) / len(vals)) for step, vals in step_values.items()
                )
                for key, step_values in step_accumulator.items()
            }

        def _common_metadata(attr: str) -> Dict[str, str]:
            key_sets = [getattr(r, attr).keys() for r in group.runs]
            common_keys = set.intersection(*map(set, key_sets))
            result = {}
            for k in common_keys:
                values = {str(getattr(r, attr)[k]) for r in group.runs}
                result[k] = next(iter(values)) if len(values) == 1 else "#"
            return result

        all_metrics = [r.metrics for r in group.runs]
        all_keys = set().union(*all_metrics)
        mean_metrics = {
            k: _mean([m[k] for m in all_metrics if k in m]) for k in all_keys
        }

        return Run(
            id=f"grouped:{group.key}:{group.value}",
            params=_common_metadata("params"),
            metrics=mean_metrics,
            temporal=_mean_temporal(group.runs),
        )

    def _to_query(self) -> Query:
        from .query import Query

        return Query([run for group in self._grouped for run in group.runs])

    def all(self) -> List[Run]:
        """Collect all runs in the grouped query by flattening the grouped runs.

        Returns:
            A list of all runs in the grouped query.
        """
        return deepcopy(self._to_query()._runs)

    def copy(self) -> GroupedQuery:
        """Obtain a shallow copy of the grouped query.

        Returns:
            A new grouped query with the same grouped runs as the original grouped
            query.
        """
        return GroupedQuery(self._grouped[:])

    def deepcopy(self) -> GroupedQuery:
        """Obtain a deep copy of the grouped query.

        Returns:
            A new grouped query with deep copies of the grouped runs in the original
            grouped query.
        """
        return GroupedQuery(deepcopy(self._grouped))

    def __len__(self) -> int:
        """Get the number of grouped runs in the grouped query.

        Returns:
            The number of grouped runs in the grouped query.
        """
        return len(self._grouped)
