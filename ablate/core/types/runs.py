from typing import Any, Dict, List, Tuple

from pydantic import BaseModel


class Run(BaseModel):
    id: str
    params: Dict[str, Any]
    metrics: Dict[str, float]
    temporal: Dict[str, list[Tuple[int, float]]] = {}

    def __init__(
        self,
        id: str,
        params: Dict[str, Any],
        metrics: Dict[str, float],
        temporal: Dict[str, list[Tuple[int, float]]] | None = None,
    ) -> None:  # sphinx needs an explicit __init__ for autodoc
        """A single run of an experiment.

        Args:
            id: Unique identifier for the run.
            params: Parameters used for the run.
            metrics: Metrics recorded during the run.
            temporal: Temporal data recorded during the run. If None, an empty
                dictionary is used. Defaults to None.
        """
        super().__init__(id=id, params=params, metrics=metrics, temporal=temporal or {})


class GroupedRun(BaseModel):
    key: str
    value: str
    runs: List[Run]

    def __init__(
        self,
        key: str,
        value: str,
        runs: List[Run],
    ) -> None:  # sphinx needs an explicit __init__ for autodoc
        """A collection of runs grouped by a key-value pair.

        Args:
            key: Key used to group the runs.
            value: Value used to group the runs.
            runs: List of runs that belong to this group.
        """
        super().__init__(key=key, value=value, runs=runs)
