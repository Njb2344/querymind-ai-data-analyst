"""
chart_generator.py

Generates polished charts using matplotlib and seaborn.
"""

import logging
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

from config.settings import CHART_FIGSIZE, CHART_OUTPUT_DIR, CHART_DPI

logger = logging.getLogger(__name__)

OUTPUT_DIR = Path(CHART_OUTPUT_DIR)

# --- Professional dark theme ---
DARK_BG = "#0E1117"
CARD_BG = "#1A1D23"
TEXT_COLOR = "#FAFAFA"
ACCENT = "#4F8BF9"
ACCENT_2 = "#636EFA"
GRID_COLOR = "#2A2D35"

plt.rcParams.update({
    "figure.facecolor": DARK_BG,
    "axes.facecolor": CARD_BG,
    "axes.edgecolor": GRID_COLOR,
    "axes.labelcolor": TEXT_COLOR,
    "text.color": TEXT_COLOR,
    "xtick.color": TEXT_COLOR,
    "ytick.color": TEXT_COLOR,
    "grid.color": GRID_COLOR,
    "grid.alpha": 0.3,
    "font.family": "sans-serif",
    "font.size": 11,
})


def get_next_chart_path() -> Path:
    """Generate the next chart filename."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    existing = list(OUTPUT_DIR.glob("chart_*.png"))

    if not existing:
        next_id = 1
    else:
        ids = []
        for f in existing:
            try:
                ids.append(int(f.stem.split("_")[1]))
            except (ValueError, IndexError):
                continue
        next_id = max(ids, default=0) + 1

    return OUTPUT_DIR / f"chart_{next_id:03d}.png"


def _truncate_labels(labels, max_len=18):
    """Shorten long axis labels."""
    return [
        (str(l)[:max_len] + "..." if len(str(l)) > max_len else str(l))
        for l in labels
    ]


def generate_chart(df, chart_type: str) -> str:
    """
    Generate a polished chart from dataframe results.

    Parameters
    ----------
    df : pandas.DataFrame
    chart_type : str
        "bar", "line", or "scatter"

    Returns
    -------
    str or None
        Path of saved chart image, or None.
    """
    if df.empty:
        logger.warning("Cannot generate chart: dataframe is empty.")
        return None

    numeric_cols = df.select_dtypes(include="number").columns
    categorical_cols = df.select_dtypes(include="object").columns

    chart_path = get_next_chart_path()

    try:
        fig, ax = plt.subplots(figsize=CHART_FIGSIZE)
        ax.grid(True, axis="y", alpha=0.2)

        if chart_type == "bar":
            if len(numeric_cols) < 1 or len(categorical_cols) < 1:
                plt.close(fig)
                return None

            numeric_col = numeric_cols[0]
            categorical_col = categorical_cols[0]

            # Limit to top 15 for readability
            plot_df = df.nlargest(15, numeric_col) if len(df) > 15 else df
            labels = _truncate_labels(plot_df[categorical_col])

            palette = sns.color_palette([ACCENT, ACCENT_2], n_colors=len(plot_df))
            bars = ax.barh(
                y=range(len(plot_df)),
                width=plot_df[numeric_col].values,
                color=palette,
                edgecolor="none",
                height=0.6
            )

            ax.set_yticks(range(len(plot_df)))
            ax.set_yticklabels(labels, fontsize=10)
            ax.invert_yaxis()
            ax.set_xlabel(numeric_col.replace("_", " ").title(), fontsize=11)
            ax.set_title(
                f"{numeric_col.replace('_', ' ').title()} by "
                f"{categorical_col.replace('_', ' ').title()}",
                fontsize=14, fontweight="bold", pad=15
            )
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

        elif chart_type == "line":
            if len(numeric_cols) < 1:
                plt.close(fig)
                return None

            numeric_col = numeric_cols[0]

            ax.plot(
                df.index, df[numeric_col],
                color=ACCENT, linewidth=2.5, marker="o",
                markersize=5, markerfacecolor="white",
                markeredgecolor=ACCENT, markeredgewidth=1.5
            )
            ax.fill_between(
                df.index, df[numeric_col],
                alpha=0.1, color=ACCENT
            )
            ax.set_title(
                f"Trend of {numeric_col.replace('_', ' ').title()}",
                fontsize=14, fontweight="bold", pad=15
            )
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

        elif chart_type == "scatter":
            if len(numeric_cols) < 2:
                plt.close(fig)
                return None

            ax.scatter(
                df[numeric_cols[0]], df[numeric_cols[1]],
                color=ACCENT, alpha=0.7, s=50, edgecolors="white",
                linewidths=0.5
            )
            ax.set_xlabel(
                numeric_cols[0].replace("_", " ").title(), fontsize=11
            )
            ax.set_ylabel(
                numeric_cols[1].replace("_", " ").title(), fontsize=11
            )
            ax.set_title(
                f"{numeric_cols[1].replace('_', ' ').title()} vs "
                f"{numeric_cols[0].replace('_', ' ').title()}",
                fontsize=14, fontweight="bold", pad=15
            )
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

        else:
            plt.close(fig)
            return None

        plt.tight_layout()
        plt.savefig(chart_path, dpi=CHART_DPI, bbox_inches="tight")
        plt.close(fig)

        logger.info("Chart saved to: %s", chart_path)
        return str(chart_path)

    except Exception as e:
        logger.error("Failed to generate chart: %s", e)
        plt.close("all")
        return None
