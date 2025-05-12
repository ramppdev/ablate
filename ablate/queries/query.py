from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
import hashlib
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Set, Tuple, Union

from ablate.core.types import GroupedRun, Run

from .grouped_query import GroupedQuery


if TYPE_CHECKING:  # pragma: no cover
    from .selectors import AbstractMetric, AbstractParam


class Query:
    def __init__(self, runs: List[Run]) -> None:
        """Query interface for manipulating runs in a functional way.

        All methods operate on a shallow copy of the runs in the query, so the original
        runs are not modified and assumed to be immutable.

        Args:
            runs: List of runs to be queried.
        """
        self._runs = runs

    def filter(self, fn: Callable[[Run], bool]) -> Query:
        """Filter the runs in the query based on a predicate function.

        Args:
            fn: Predicate function that takes in a run and returns a boolean value.

        Returns:
            A new query with the runs that satisfy the predicate function.
        """
        return Query([r for r in self._runs[:] if fn(r)])

    def map(self, fn: Callable[[Run], Run]) -> Query:
        """Apply a function to each run in the query.

        This function is intended to be used for modifying the runs in the query. The
        function should return a new run object as the original run is not modified.

        Args:
            fn: Function that takes in a run and returns a new run object.

        Returns:
            A new query with the modified runs.
        """
        return Query([fn(r) for r in deepcopy(self._runs)])

    def sort(self, key: AbstractMetric, ascending: bool = False) -> Query:
        """Sort the runs in the query based on a metric.

        Args:
            key: Metric to sort the runs by.
            ascending: Whether to sort in ascending order.
                Defaults to False (descending order).

        Returns:
            A new query with the runs sorted by the specified metric.
        """
        return Query(sorted(self._runs[:], key=key, reverse=not ascending))

    def project(self, selectors: Union[AbstractParam, List[AbstractParam]]) -> Query:
        """Project the parameter space of the runs in the query to a subset of
        parameters only including the specified selectors.

        This function is intended to be used for reducing the dimensionality of the
        parameter space and therefore operates on a deep copy of the runs in the query.

        Args:
            selectors: Selector or list of selectors to project the runs by.

        Returns:
            A new query with the projected runs.
        """
        if not isinstance(selectors, list):
            selectors = [selectors]

        names = {s.name for s in selectors}
        projected: List[Run] = []

        for run in deepcopy(self._runs):
            run.params = {k: v for k, v in run.params.items() if k in names}
            projected.append(run)

        return Query(projected)

    def groupby(
        self,
        selectors: Union[AbstractParam, List[AbstractParam]],
    ) -> GroupedQuery:
        """Group the runs in the query by one or more selectors.

        Args:
            selectors: Selector or list of selectors to group the runs by.

        Returns:
            A grouped query containing the grouped runs.
        """
        if not isinstance(selectors, list):
            selectors = [selectors]

        def key_fn(run: Run) -> Tuple[Any, ...]:
            return tuple(selector(run) for selector in selectors)

        groups = defaultdict(list)
        for run in self._runs:
            groups[key_fn(run)].append(run)

        grouped = [
            GroupedRun(
                key="+".join(selector.name for selector in selectors),
                value="|".join(map(str, k)),
                runs=v,
            )
            for k, v in groups.items()
        ]
        return GroupedQuery(grouped)

    def groupdiff(
        self,
        selectors: Union[AbstractParam, List[AbstractParam]],
    ) -> GroupedQuery:
        """Group the runs in the query by one or more selectors, excluding the keys.
        This is similar to `groupby` but it excludes the specified keys from the
        grouping key.

        Args:
            selectors: Selector or list of selectors to exclude from the grouping key.

        Returns:
            A grouped query containing the grouped runs.
        """
        if not isinstance(selectors, list):
            selectors = [selectors]

        def exclude_keys(
            d: Dict[str, Any],
            keys: Set[str],
        ) -> Tuple[Tuple[str, Any], ...]:
            return tuple(sorted((k, v) for k, v in d.items() if k not in keys))

        exclude_names = {s.name for s in selectors}
        groups = defaultdict(list)
        for run in self._runs:
            key = exclude_keys(run.params, exclude_names)
            groups[key].append(run)

        def _hash_key(kv: Tuple[Tuple[str, Any], ...]) -> str:
            raw = ",".join(f"{k}={v}" for k, v in sorted(kv))
            return hashlib.md5(raw.encode()).hexdigest()[:8]

        grouped = [
            GroupedRun(
                key="-".join(s.name for s in selectors),
                value=_hash_key(k),
                runs=runs,
            )
            for k, runs in groups.items()
        ]
        return GroupedQuery(grouped)

    def head(self, n: int) -> Query:
        """Get the first n runs in the query.

        Args:
            n: Number of runs to return.

        Returns:
            A new query with the first n runs.
        """
        return Query(self._runs[:n])

    def tail(self, n: int) -> Query:
        """Get the last n runs in the query.

        Args:
            n: Number of runs to return.

        Returns:
            A new query with the last n runs.
        """
        return Query(self._runs[-n:])

    def topk(self, metric: AbstractMetric, k: int) -> Query:
        """Get the top k runs in the query based on a metric.

        Args:
            metric: Metric to sort the runs by.
            k: Number of top runs to return.

        Returns:
            A new query with the top k runs based on the specified metric.
        """
        return self.sort(metric, ascending=metric.direction == "min").head(k)

    def bottomk(self, metric: AbstractMetric, k: int) -> Query:
        """Get the bottom k runs in the query based on a metric.

        Args:
            metric: Metric to sort the runs by.
            k: Number of bottom runs to return.

        Returns:
            A new query with the bottom k runs based on the specified metric.
        """
        return self.sort(metric, ascending=metric.direction == "max").head(k)

    def all(self) -> List[Run]:
        """Collect all runs in the query.

        Returns:
            A list of all runs in the query.
        """
        return deepcopy(self._runs)

    def copy(self) -> Query:
        """Obtain a shallow copy of the query.

        Returns:
            A new query with the same runs as the original query.
        """
        return Query(self._runs[:])

    def deepcopy(self) -> Query:
        """Obtain a deep copy of the query.

        Returns:
            A new query with deep copies of the runs in the original query.
        """
        return Query(deepcopy(self._runs))

    def __len__(self) -> int:
        """Get the number of runs in the query.

        Returns:
            The number of runs in the query.
        """
        return len(self._runs)
