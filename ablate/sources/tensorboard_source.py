from pathlib import Path
from typing import List

from ablate.core.types import Run

from .abstract_source import AbstractSource


class TensorBoard(AbstractSource):
    def __init__(self, logdirs: str | List[str]) -> None:
        """TensorBoard source for loading runs from event logs.

        Args:
            logdirs: A path or list of paths to TensorBoard event log directories.
        """
        try:
            from tensorboard.backend.event_processing import (
                event_accumulator,  # noqa: F401
            )
        except ImportError as e:
            raise ImportError(
                "TensorBoard source requires `tensorboard`. "
                "Please install with `pip install ablate[tensorboard]`."
            ) from e

        self.logdirs = (
            [Path(logdirs)] if isinstance(logdirs, str) else [Path(p) for p in logdirs]
        )

    def load(self) -> List[Run]:
        from tensorboard.backend.event_processing.event_accumulator import (
            EventAccumulator,
        )

        records: List[Run] = []

        for logdir in self.logdirs:
            for path in logdir.glob("**/events.out.tfevents.*"):
                ea = EventAccumulator(str(path.parent))
                ea.Reload()

                metrics = {}
                temporal = {}

                for tag in ea.Tags().get("scalars", []):
                    scalar_events = ea.Scalars(tag)
                    if scalar_events:
                        last_value = scalar_events[-1].value
                        metrics[tag] = last_value
                        temporal[tag] = [(e.step, e.value) for e in scalar_events]

                run_id = path.parent.name  # use folder name as ID

                records.append(
                    Run(id=run_id, params={}, metrics=metrics, temporal=temporal)
                )

        return records
