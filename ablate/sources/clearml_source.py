from typing import List

from ablate.core.types import Run

from .abstract_source import AbstractSource


class ClearML(AbstractSource):
    def __init__(self, project_name: str) -> None:
        """ClearML source for loading runs from a ClearML server.

        Args:
            project_name: The name of the ClearML project to load runs from.

        Raises:
            ImportError: If the `clearml` package is not installed.
        """
        try:
            from clearml import Task  # noqa: F401
        except ImportError as e:
            raise ImportError(
                "ClearML source requires `clearml`. "
                "Install via `pip install ablate[clearml]`."
            ) from e
        self.project_name = project_name

    def load(self) -> List[Run]:
        from clearml import Task

        task_ids = Task.query_tasks(project_name=self.project_name)
        records = []

        for task_id in task_ids:
            t = Task.get_task(task_id=task_id)
            params = t.get_parameters() or {}
            scalars = t.get_reported_scalars() or {}

            metrics = {}
            temporal = {}

            for _, series in scalars.items():
                for name, values in series.items():
                    if not values or "x" not in values or "y" not in values:
                        continue  # pragma: no cover
                    x, y = values["x"], values["y"]
                    if isinstance(x, list) and isinstance(y, list) and len(x) == len(y):
                        temporal[name] = list(zip(x, y, strict=False))
                        metrics[name] = float(y[-1])

            records.append(
                Run(id=t.id, params=params, metrics=metrics, temporal=temporal)
            )

        return records
