from __future__ import annotations

from abc import ABC, abstractmethod
from operator import eq, ge, gt, le, lt, ne
from typing import TYPE_CHECKING, Any, Callable, Literal


if TYPE_CHECKING:  # pragma: no cover
    from ablate.core.types import Run


class Predicate:
    def __init__(self, fn: Callable[[Run], bool]) -> None:
        self._fn = fn

    def __call__(self, run: Run) -> bool:
        return self._fn(run)

    def __and__(self, other: Predicate) -> Predicate:
        return Predicate(lambda run: self(run) and other(run))

    def __or__(self, other: Predicate) -> Predicate:
        return Predicate(lambda run: self(run) or other(run))

    def __invert__(self) -> Predicate:
        return Predicate(lambda run: not self(run))


class AbstractSelector(ABC):
    def __init__(self, name: str, label: str | None = None) -> None:
        """Abstract class for selecting runs based on a specific attribute.

        Args:
            name: Name of the attribute to select on.
            label: Optional label for displaying purposes. If None, defaults to `name`.
                Defaults to None.
        """
        self.name = name
        self.label = label or name

    @abstractmethod
    def __call__(self, run: Run) -> Any: ...

    def _cmp(self, op: Callable[[Any, Any], bool], other: Any) -> Predicate:
        return Predicate(lambda run: op(self(run), other))

    def __eq__(self, other: object) -> Predicate:  # type: ignore[override]
        return self._cmp(eq, other)

    def __ne__(self, other: object) -> Predicate:  # type: ignore[override]
        return self._cmp(ne, other)

    def __lt__(self, other: Any) -> Predicate:
        return self._cmp(lt, other)

    def __le__(self, other: Any) -> Predicate:
        return self._cmp(le, other)

    def __gt__(self, other: Any) -> Predicate:
        return self._cmp(gt, other)

    def __ge__(self, other: Any) -> Predicate:
        return self._cmp(ge, other)


class AbstractParam(AbstractSelector, ABC): ...


class Id(AbstractParam):
    def __init__(self, label: str | None = None) -> None:
        """Selector for the ID of the run.

        Args:
            label: Optional label for displaying purposes. If None, defaults to `name`.
                Defaults to None.
        """
        super().__init__("id", label)

    def __call__(self, run: Run) -> str:
        return run.id


class Param(AbstractParam):
    """Selector for a specific parameter of the run."""

    def __call__(self, run: Run) -> int | float | str | None:
        return run.params.get(self.name)


class AbstractMetric(AbstractSelector, ABC):
    def __init__(
        self,
        name: str,
        direction: Literal["min", "max"],
        label: str | None = None,
    ) -> None:
        super().__init__(name, label)
        if direction not in ("min", "max"):
            raise ValueError(
                f"Invalid direction: '{direction}'. Must be 'min' or 'max'."
            )
        self.direction = direction


class Metric(AbstractMetric):
    """Selector for a specific metric of the run.

    Args:
        name: Name of the metric to select on.
        direction: Direction of the metric. "min" for minimization, "max" for
            maximization.
        label: Optional label for displaying purposes. If None, defaults to `name`.
            Defaults to None.
    """

    def __call__(self, run: Run) -> float:
        val = run.metrics.get(self.name)
        if val is None:
            return float("-inf") if self.direction == "max" else float("inf")
        return val


class TemporalMetric(AbstractMetric):
    def __init__(
        self,
        name: str,
        direction: Literal["min", "max"],
        reduction: Literal["min", "max", "first", "last"] | None = None,
        label: str | None = None,
    ) -> None:
        """Selector for a specific temporal metric of the run.

        Args:
            name: Name of the temporal metric to select on.
            direction: Direction of the metric. "min" for minimization, "max" for
                maximization.
            reduction: Reduction method to apply to the temporal metric. "min" for
                minimum, "max" for maximum, "first" for the first value, and "last"
                for the last value. If None, the direction is used as the reduction.
                Defaults to None.
            label: Optional label for displaying purposes. If None, defaults to `name`.
                Defaults to None.
        """
        super().__init__(name, direction, label)
        if reduction is not None and reduction not in ("min", "max", "first", "last"):
            raise ValueError(
                f"Invalid reduction method: '{reduction}'. Must be 'min', 'max', "
                "'first', or 'last'."
            )
        self.reduction = reduction or direction

    def __call__(self, run: Run) -> float:
        values = run.temporal.get(self.name, [])
        if not values:
            return float("nan")

        match self.reduction:
            case "min":
                return min(v for _, v in values)
            case "max":
                return max(v for _, v in values)
            case "first":
                return values[0][1]
            case "last":
                return values[-1][1]
