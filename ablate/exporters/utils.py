import hashlib
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from ablate.blocks import H1, H2, H3, H4, H5, H6


HEADING_LEVELS = {H1: 1, H2: 2, H3: 3, H4: 4, H5: 5, H6: 6}


def apply_default_plot_style() -> None:
    sns.set_style("whitegrid")
    sns.set_context("paper", font_scale=0.8)
    sns.set_palette("muted")
    plt.rcParams["figure.dpi"] = 300


def render_metric_plot(
    df: pd.DataFrame,
    output_dir: Path,
    name_prefix: str,
) -> str | None:
    apply_default_plot_style()
    if df.empty:
        return None

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
    ax.legend(title="Run", loc="best", frameon=False)
    plt.tight_layout()

    h = hashlib.md5(df.to_csv(index=False).encode("utf-8")).hexdigest()[:12]
    filename = f"{name_prefix}_{h}.png"
    fig.savefig(output_dir / filename)
    plt.close(fig)
    return filename
