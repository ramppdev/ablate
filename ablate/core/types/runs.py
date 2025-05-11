from typing import Any, Dict, List, Tuple

from pydantic import BaseModel


class Run(BaseModel):
    """A single run of an experiment.

    Args:
        id: Unique identifier for the run.
        params: Parameters used for the run.
        metrics: Metrics recorded during the run.
        temporal: Temporal data recorded during the run.
    """

    id: str
    params: Dict[str, Any]
    metrics: Dict[str, float]
    temporal: Dict[str, list[Tuple[int, float]]] = {}


class GroupedRun(BaseModel):
    """A collection of runs grouped by a key-value pair.

    Args:
        key: Key used to group the runs.
        value: Value used to group the runs.
        runs: List of runs that belong to this group.
    """

    key: str
    value: str
    runs: List[Run]
