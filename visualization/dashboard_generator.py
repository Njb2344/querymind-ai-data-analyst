"""
dashboard_generator.py

Creates polished multi-chart dashboards with dark theme.
"""

import logging
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

from config.settings import DASHBOARD_FIGSIZE

logger = logging.getLogger(__name__)

# Dark theme colors (matching chart_generator)
DARK_BG = "#0E1117"
CARD_BG = "#1A1D23"
TEXT_COLOR = "#FAFAFA"
ACCENT = "#4F8BF9"
ACCENT_2 = "#636EFA"
GRID_COLOR = "#2A2D35"


def _truncate_labels(labels, max_len=16):
    """Shorten long axis labels."""
    return [
        (str(l)[:max_len] + "..." if len(str(l)) > max_len else str(l))
        for l in labels
    ]


def generate_dashboard(df) -> list:
    """
    Generate a dashboard with multiple polished charts.

    Parameters
    ----------
    df : pandas.DataFrame

    Returns
    -------
    list of matplotlib figures
    """
    figures = []

    if df.empty:
        logger.warning("Cannot generate dashboard: empty dataframe.")
        return figures

    numeric_cols = df.select_dtypes(include="number").columns
    categorical_cols = df.select_dtypes(include="object").columns

    try:
        # Chart 1 - Horizontal bar (top 12)
        if len(numeric_cols) >= 1 and len(categorical_cols) >= 1:
            fig1, ax = plt.subplots(figsize=DASHBOARD_FIGSIZE)
            fig1.patch.set_facecolor(DARK_BG)
            ax.set_facecolor(CARD_BG)

            plot_df = df.nlargest(12, numeric_cols[0]) if len(df) > 12 else df
            labels = _truncate_labels(plot_df[categorical_cols[0]])

            ax.barh(
                y=range(len(plot_df)),
                width=plot_df[numeric_cols[0]].values,
                color=ACCENT, edgecolor="none", height=0.6
            )
            ax.set_yticks(range(len(plot_df)))
            ax.set_yticklabels(labels, fontsize=9, color=TEXT_COLOR)
            ax.invert_yaxis()
            ax.set_title(
                f"{numeric_cols[0].replace('_', ' ').title()} by "
                f"{categorical_cols[0].replace('_', ' ').title()}",
                fontsize=12, fontweight="bold", color=TEXT_COLOR, pad=12
            )
            ax.tick_params(colors=TEXT_COLOR)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["left"].set_color(GRID_COLOR)
            ax.spines["bottom"].set_color(GRID_COLOR)
            ax.grid(True, axis="x", alpha=0.15, color=GRID_COLOR)
            plt.tight_layout()
            figures.append(fig1)

        # Chart 2 - Distribution
        if len(numeric_cols) >= 1:
            fig2, ax = plt.subplots(figsize=DASHBOARD_FIGSIZE)
            fig2.patch.set_facecolor(DARK_BG)
            ax.set_facecolor(CARD_BG)

            sns.histplot(
                df[numeric_cols[0]], kde=True, ax=ax,
                color=ACCENT, edgecolor=CARD_BG, alpha=0.7
            )
            ax.set_title(
                f"Distribution of {numeric_cols[0].replace('_', ' ').title()}",
                fontsize=12, fontweight="bold", color=TEXT_COLOR, pad=12
            )
            ax.tick_params(colors=TEXT_COLOR)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["left"].set_color(GRID_COLOR)
            ax.spines["bottom"].set_color(GRID_COLOR)
            ax.set_xlabel("", color=TEXT_COLOR)
            ax.set_ylabel("", color=TEXT_COLOR)
            plt.tight_layout()
            figures.append(fig2)

        # Chart 3 - Trend line
        if len(df) > 5 and len(numeric_cols) >= 1:
            fig3, ax = plt.subplots(figsize=DASHBOARD_FIGSIZE)
            fig3.patch.set_facecolor(DARK_BG)
            ax.set_facecolor(CARD_BG)

            ax.plot(
                df.index, df[numeric_cols[0]],
                color=ACCENT, linewidth=2, marker="o",
                markersize=4, markerfacecolor="white",
                markeredgecolor=ACCENT, markeredgewidth=1.5
            )
            ax.fill_between(
                df.index, df[numeric_cols[0]],
                alpha=0.08, color=ACCENT
            )
            ax.set_title(
                f"Trend of {numeric_cols[0].replace('_', ' ').title()}",
                fontsize=12, fontweight="bold", color=TEXT_COLOR, pad=12
            )
            ax.tick_params(colors=TEXT_COLOR)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["left"].set_color(GRID_COLOR)
            ax.spines["bottom"].set_color(GRID_COLOR)
            ax.grid(True, axis="y", alpha=0.15, color=GRID_COLOR)
            plt.tight_layout()
            figures.append(fig3)

    except Exception as e:
        logger.error("Error generating dashboard chart: %s", e)
        plt.close("all")

    logger.info("Dashboard generated with %d charts.", len(figures))
    return figures
