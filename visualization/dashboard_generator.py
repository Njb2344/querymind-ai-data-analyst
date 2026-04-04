"""
dashboard_generator.py

Creates multi-chart dashboards from a dataframe
to simulate an AI analytics dashboard.
"""

import logging
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from config.settings import DASHBOARD_FIGSIZE

logger = logging.getLogger(__name__)


def generate_dashboard(df) -> list:
    """
    Generate a dashboard with multiple chart types.

    Parameters
    ----------
    df : pandas.DataFrame
        The query results to visualize.

    Returns
    -------
    list
        List of matplotlib figures.
    """
    figures = []

    if df.empty:
        logger.warning("Cannot generate dashboard: empty dataframe.")
        return figures

    numeric_cols = df.select_dtypes(include="number").columns
    categorical_cols = df.select_dtypes(include="object").columns

    try:
        # Chart 1 - Bar chart
        if len(numeric_cols) >= 1 and len(categorical_cols) >= 1:
            fig1, ax = plt.subplots(figsize=DASHBOARD_FIGSIZE)
            sns.barplot(
                x=df[categorical_cols[0]],
                y=df[numeric_cols[0]],
                ax=ax
            )
            ax.set_title(f"{numeric_cols[0]} by {categorical_cols[0]}")
            plt.xticks(rotation=45)
            plt.tight_layout()
            figures.append(fig1)

        # Chart 2 - Distribution
        if len(numeric_cols) >= 1:
            fig2, ax = plt.subplots(figsize=DASHBOARD_FIGSIZE)
            sns.histplot(df[numeric_cols[0]], kde=True, ax=ax)
            ax.set_title(f"Distribution of {numeric_cols[0]}")
            plt.tight_layout()
            figures.append(fig2)

        # Chart 3 - Trend (if enough rows)
        if len(df) > 5 and len(numeric_cols) >= 1:
            fig3, ax = plt.subplots(figsize=DASHBOARD_FIGSIZE)
            sns.lineplot(x=df.index, y=df[numeric_cols[0]], ax=ax)
            ax.set_title(f"Trend of {numeric_cols[0]}")
            plt.tight_layout()
            figures.append(fig3)

    except Exception as e:
        logger.error("Error generating dashboard chart: %s", e)
        plt.close("all")

    logger.info("Dashboard generated with %d charts.", len(figures))
    return figures
