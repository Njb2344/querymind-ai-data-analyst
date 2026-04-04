"""
chart_generator.py

Generates charts using matplotlib and seaborn.

Input:  dataframe + chart type
Output: saved chart image path
"""

import logging
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

from config.settings import CHART_FIGSIZE, CHART_OUTPUT_DIR, CHART_DPI

logger = logging.getLogger(__name__)

OUTPUT_DIR = Path(CHART_OUTPUT_DIR)


def get_next_chart_path() -> Path:
    """
    Generate the next chart filename automatically.

    Returns
    -------
    Path
        Path for the next chart file.
    """
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


def generate_chart(df, chart_type: str) -> str:
    """
    Generate a chart from dataframe results.

    Parameters
    ----------
    df : pandas.DataFrame
        Query result dataframe.
    chart_type : str
        Type of chart to generate (bar, line, scatter).

    Returns
    -------
    str or None
        Path of saved chart image, or None if chart cannot be generated.
    """
    if df.empty:
        logger.warning("Cannot generate chart: dataframe is empty.")
        return None

    numeric_cols = df.select_dtypes(include="number").columns
    categorical_cols = df.select_dtypes(include="object").columns

    chart_path = get_next_chart_path()

    try:
        fig, ax = plt.subplots(figsize=CHART_FIGSIZE)

        if chart_type == "bar":
            if len(numeric_cols) < 1 or len(categorical_cols) < 1:
                logger.warning("Not enough columns for bar chart.")
                plt.close(fig)
                return None

            numeric_col = numeric_cols[0]
            categorical_col = categorical_cols[0]

            sns.barplot(
                x=df[categorical_col],
                y=df[numeric_col],
                ax=ax
            )
            ax.set_xlabel(categorical_col)
            ax.set_ylabel(numeric_col)
            ax.set_title(f"{numeric_col} by {categorical_col}")

        elif chart_type == "line":
            if len(numeric_cols) < 1:
                logger.warning("Not enough numeric columns for line chart.")
                plt.close(fig)
                return None

            numeric_col = numeric_cols[0]

            sns.lineplot(x=df.index, y=df[numeric_col], ax=ax)
            ax.set_title(f"Trend of {numeric_col}")

        elif chart_type == "scatter":
            if len(numeric_cols) < 2:
                logger.warning("Not enough numeric columns for scatter plot.")
                plt.close(fig)
                return None

            sns.scatterplot(
                x=df[numeric_cols[0]],
                y=df[numeric_cols[1]],
                ax=ax
            )
            ax.set_title(f"{numeric_cols[1]} vs {numeric_cols[0]}")

        else:
            logger.info("Chart type '%s' not supported, skipping.", chart_type)
            plt.close(fig)
            return None

        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(chart_path, dpi=CHART_DPI)
        plt.close(fig)

        logger.info("Chart saved to: %s", chart_path)
        return str(chart_path)

    except Exception as e:
        logger.error("Failed to generate chart: %s", e)
        plt.close("all")
        return None
