import itertools
from typing import Dict, List

import numpy as np

from ablate.core.types import Run

from .abstract_source import AbstractSource


class Mock(AbstractSource):
    def __init__(
        self,
        grid: Dict[str, List[str | int | float | bool]],
        num_seeds: int = 1,
        steps: int = 25,
    ) -> None:
        """Mock source for generating runs based on a grid of hyperparameters.

        For each run, `accuracy`, `f1`, and `loss` metrics are randomly generated.

        Args:
            grid: Dictionary mapping parameter names to lists of values.
            num_seeds: Number of runs to generate per config with different seeds.
                Defaults to 1.
            steps: Number of steps to use for temporal metrics.
                Defaults to 25.
        """
        self.grid = grid
        self.num_seeds = num_seeds
        self.steps = steps

    def _generate_runs(
        self,
        param_dict: Dict[str, str | int | float | bool],
        idx: int,
    ) -> List[Run]:
        runs: List[Run] = []
        for local_seed in range(self.num_seeds):
            global_seed = idx * self.num_seeds + local_seed
            rng = np.random.default_rng(global_seed)
            steps = np.arange(1, self.steps + 1, dtype=np.int32)

            progress = steps / self.steps
            growth = 1 / (1 + np.exp(-6 * (progress - 0.5)))
            _accc = 0.6 + 0.35 * growth + rng.normal(0, 0.01, len(steps))
            accc = np.clip(_accc, 0.0, 1.0)
            _f1c = accc - rng.uniform(0.01, 0.05, len(steps))
            f1c = np.clip(_f1c, 0.0, 1.0)
            _lossc = 1.5 / (steps + 1) + rng.uniform(0.01, 0.05, len(steps))
            lossc = np.clip(_lossc, 1e-4, None)

            accuracy = float(np.round(accc[-1], 4))
            f1 = float(np.round(f1c[-1], 4))
            loss = float(np.round(lossc[-1], 4))

            params = {
                **{k: str(v) for k, v in param_dict.items()},
                "seed": str(local_seed),
            }
            rid = f"{'_'.join(f'{k}={v}' for k, v in params.items())}"
            m = {"accuracy": accuracy, "f1": f1, "loss": loss}
            t = {
                "accuracy": list(zip(steps.tolist(), accc.tolist(), strict=False)),
                "f1": list(zip(steps.tolist(), f1c.tolist(), strict=False)),
                "loss": list(zip(steps.tolist(), lossc.tolist(), strict=False)),
            }
            runs.append(Run(id=rid, params=params, metrics=m, temporal=t))
        return runs

    def load(self) -> List[Run]:
        param_names = list(self.grid.keys())
        param_product = list(itertools.product(*[self.grid[k] for k in param_names]))
        runs: List[Run] = []

        for idx, product in enumerate(param_product):
            param_dict = dict(zip(param_names, product, strict=False))
            runs.extend(self._generate_runs(param_dict, idx))

        return runs
