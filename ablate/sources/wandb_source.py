from typing import List

import pandas as pd

from ablate.core.types import Run

from .abstract_source import AbstractSource


class WandB(AbstractSource):
    def __init__(self, project: str, entity: str | None = None) -> None:
        """Weights & Biases (WandB) source for loading runs from a WandB project.

        Args:
            project: The name of the WandB project to load runs from.
            entity: Optional WandB entity (team or user). If None, uses the default
                entity from the WandB configuration. Defaults to None.

        Raises:
            ImportError: If the `wandb` package is not installed.
        """

        try:
            import wandb
        except ImportError as e:
            raise ImportError(
                "Wandb source requires `wandb`. "
                "Install via `pip install ablate[wandb]`."
            ) from e
        self.project = project
        self.entity = entity or wandb.Api().default_entity
        self.api = wandb.Api()

    def load(self) -> List[Run]:
        runs = self.api.runs(f"{self.entity}/{self.project}")
        records = []
        for r in runs:
            params = dict(r.config)
            metrics = {
                k: v for k, v in r.summary.items() if isinstance(v, (int, float))
            }
            temporal = {}
            for key in metrics:
                df = r.history(keys=[key])
                if (
                    isinstance(df, pd.DataFrame)
                    and key in df.columns
                    and "_step" in df.columns
                ):
                    temporal[key] = list(zip(df["_step"], df[key], strict=False))

            records.append(
                Run(id=r.id, params=params, metrics=metrics, temporal=temporal)
            )
        return records
