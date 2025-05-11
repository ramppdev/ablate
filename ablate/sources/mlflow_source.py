from pathlib import Path
from typing import List

from ablate.core.types import Run

from .abstract_source import AbstractSource


class MLflow(AbstractSource):
    def __init__(self, tracking_uri: str, experiment_names: List[str]) -> None:
        try:
            from mlflow.tracking import MlflowClient
        except ImportError as e:
            raise ImportError(
                "MLflow source requires `mlflow`. "
                "Please install with `pip install ablate[mlflow]`."
            ) from e

        self.tracking_uri = tracking_uri
        self.experiment_names = experiment_names
        self.client = MlflowClient(Path(tracking_uri).resolve().as_uri())

    def load(self) -> List[Run]:
        runs = self.client.search_runs(
            [
                self.client.get_experiment_by_name(n).experiment_id
                for n in self.experiment_names
            ]
        )
        records: List[Run] = []
        for run in runs:
            p, m, t = run.data.params, run.data.metrics, {}
            p.update(run.data.tags)
            for name in m:
                history = self.client.get_metric_history(run.info.run_id, name)
                t[name] = [(h.step, h.value) for h in history]
            records.append(Run(id=run.info.run_id, params=p, metrics=m, temporal=t))
        return records
