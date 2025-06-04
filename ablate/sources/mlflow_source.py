from pathlib import Path
from typing import List
from urllib.parse import urlparse

from ablate.core.types import Run

from .abstract_source import AbstractSource


class MLflow(AbstractSource):
    def __init__(
        self,
        experiment_names: str | List[str],
        tracking_uri: str | None,
    ) -> None:
        """MLflow source for loading runs from a MLflow server.

        Args:
            experiment_names: An experiment name or a list of experiment names to load
                runs from.
            tracking_uri: The URI or local path to the MLflow tracking server.
                If None, use the default tracking URI set in the MLflow configuration.
                Defaults to None.

        Raises:
            ImportError: If the `mlflow` package is not installed.
        """
        try:
            from mlflow.tracking import MlflowClient
        except ImportError as e:
            raise ImportError(
                "MLflow source requires `mlflow`. "
                "Install via `pip install ablate[mlflow]`."
            ) from e

        self.tracking_uri = tracking_uri
        self.experiment_names = (
            [experiment_names]
            if isinstance(experiment_names, str)
            else experiment_names
        )
        if not tracking_uri:
            self.client = MlflowClient()
            return
        if urlparse(tracking_uri).scheme in {"http", "https", "file"}:
            uri = tracking_uri
        else:
            uri = Path(tracking_uri).resolve().as_uri()
        self.client = MlflowClient(uri)

    def load(self) -> List[Run]:
        ids = [self.client.get_experiment_by_name(n) for n in self.experiment_names]
        if not all(ids):
            raise ValueError(
                f"One or more experiment names not found: {self.experiment_names}"
            )
        runs = self.client.search_runs([e.experiment_id for e in ids if e])
        records: List[Run] = []
        for run in runs:
            p, m, t = run.data.params, run.data.metrics, {}
            p.update(run.data.tags)
            for name in m:
                history = self.client.get_metric_history(run.info.run_id, name)
                t[name] = [(h.step, h.value) for h in history]
            records.append(Run(id=run.info.run_id, params=p, metrics=m, temporal=t))
        return records
