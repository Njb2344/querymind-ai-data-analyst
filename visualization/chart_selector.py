"""
chart_selector.py

Determines the best chart type based on
the structure of the dataframe returned from SQL.
"""

import logging
import pandas as pd

logger = logging.getLogger(__name__)


def select_chart(df: pd.DataFrame) -> str:
    """
    Determine the best chart type for the dataframe.

    Parameters
    ----------
    df : pandas.DataFrame

    Returns
    -------
    str
        Chart type: "bar", "line", "scatter", or "table"
    """
    if df.empty:
        logger.info("Empty dataframe, defaulting to table.")
        return "table"

    numeric_cols = df.select_dtypes(include="number").columns
    categorical_cols = df.select_dtypes(include="object").columns

    # Category + metric -> bar chart
    if len(numeric_cols) >= 1 and len(categorical_cols) >= 1:
        logger.info("Selected chart type: bar")
        return "bar"

    # Time series detection
    for col in df.columns:
        if "date" in col.lower() or "time" in col.lower() or "month" in col.lower():
            logger.info("Selected chart type: line (time-based column detected)")
            return "line"

    # Two numeric columns -> scatter
    if len(numeric_cols) >= 2:
        logger.info("Selected chart type: scatter")
        return "scatter"

    logger.info("No suitable chart type found, defaulting to table.")
    return "table"
