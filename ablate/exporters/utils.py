import hashlib
from pathlib import Path
from typing import List

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from ablate.blocks import H1, H2, H3, H4, H5, H6, MetricPlot
from ablate.core.types.runs import Run


HEADING_LEVELS = {H1: 1, H2: 2, H3: 3, H4: 4, H5: 5, H6: 6}


def apply_default_plot_style() -> None:
    sns.set_style("whitegrid")
    sns.set_context("paper", font_scale=0.8)
    sns.set_palette("muted")
    plt.rcParams["figure.dpi"] = 300


def hash_dataframe(df: pd.DataFrame) -> str:
    return hashlib.md5(df.to_csv(index=False).encode("utf-8")).hexdigest()[:12]


def create_metric_plot(df: pd.DataFrame, label: str) -> plt.Figure:
    apply_default_plot_style()
    fig, ax = plt.subplots()
    sns.lineplot(
        data=df,
        x="step",
        y="value",
        hue="run",
        style="metric" if df["metric"].nunique() > 1 else None,
        ax=ax,
    )
    ax.set_xlabel("Step")
    ax.set_ylabel("Value")
    ax.legend(title=label, loc="best", frameon=False)
    plt.tight_layout()
    return fig


def render_metric_plot(
    block: MetricPlot,
    runs: List[Run],
    output_dir: Path,
) -> str | None:
    df = block.build(runs)
    if df.empty:
        return None

    fig = create_metric_plot(df, block.identifier.label)
    filename = f"{type(block).__name__}_{hash_dataframe(df)}.png"
    fig.savefig(output_dir / filename)
    plt.close(fig)
    return filename
