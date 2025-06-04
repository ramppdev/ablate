from pathlib import Path
from typing import Any, Dict, Generator, List, Union

import pandas as pd
import yaml

from ablate.core.types import Run

from .abstract_source import AbstractSource


def extract_metric_values(metrics: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
    prefix = f"{prefix}_" if prefix else ""
    return {f"{prefix}{k}": v["all"] for k, v in metrics.items() if k != "iteration"}


def flatten_autrainer_config(
    config: Union[Dict, list],
    prefix: str = "",
) -> Generator[tuple[str, Any], None, None]:
    if isinstance(config, dict):
        id_value = config.get("id")
        if "id" in config and len(config) == 1:
            yield prefix.rstrip("."), id_value
            return
        for key, value in config.items():
            if key == "id":
                yield prefix.rstrip("."), value
                continue
            yield from flatten_autrainer_config(value, f"{prefix}{key}.")
    elif isinstance(config, list):
        for idx, item in enumerate(config):
            yield from flatten_autrainer_config(item, f"{prefix}{idx}.")
    else:
        yield prefix.rstrip("."), config


class Autrainer(AbstractSource):
    def __init__(self, results_dir: str, experiment_id: str) -> None:
        """Autrainer source for loading runs from an autrainer experiment.

        Analogous to `autrainer`, all metrics are reported at the iteration where the
        tracking metric reaches its best development value.

        Args:
            results_dir: The directory where autrainer results are stored.
            experiment_id: The ID of the autrainer experiment to load.

        Raises:
            FileNotFoundError: If the specified experiment ID does not exist in the
                results directory.
        """
        self.results_dir = results_dir
        self.experiment_id = experiment_id
        self._location = Path(results_dir) / experiment_id / "training"
        if not self._location.exists():
            raise FileNotFoundError(
                "No autrainer experiment found with ID "
                f"'{experiment_id}' in directory '{results_dir}'."
            )

    def _load_run(self, path: Path) -> Run:
        run_id = path.name

        with open(path / ".hydra" / "config.yaml") as f:
            params = dict(flatten_autrainer_config(yaml.safe_load(f)))

        with open(path / "_best" / "dev.yaml") as f:
            dev_metrics = extract_metric_values(yaml.safe_load(f))
        with open(path / "_test" / "test_holistic.yaml") as f:
            test_metrics = extract_metric_values(yaml.safe_load(f), "test")
        metrics = {**dev_metrics, **test_metrics}

        df = pd.read_csv(path / "metrics.csv")
        temporal = {
            col: list(zip(df["iteration"], df[col], strict=False))
            for col in df.columns
            if col != "iteration"
        }

        return Run(id=run_id, params=params, metrics=metrics, temporal=temporal)

    def load(self) -> List[Run]:
        runs = []
        for p in Path(self._location).iterdir():
            if not p.is_dir():
                continue
            runs.append(self._load_run(p))
        return runs
