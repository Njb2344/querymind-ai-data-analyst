"""
chart_selector.py

This module decides which chart type should be generated
based on the structure of the dataframe returned from SQL.
"""

import pandas as pd


def select_chart(df):
    """
    Determine the best chart type for the dataframe.

    Parameters
    ----------
    df : pandas.DataFrame

    Returns
    -------
    str
        Chart type
    """

    # If dataframe empty → nothing to plot
    if df.empty:
        return "table"

    # Detect numeric columns
    numeric_cols = df.select_dtypes(include="number").columns

    # Detect categorical columns
    categorical_cols = df.select_dtypes(include="object").columns

    # Category + metric → bar chart
    if len(numeric_cols) >= 1 and len(categorical_cols) >= 1:
        return "bar"

    # Time series
    for col in df.columns:
        if "date" in col.lower() or "time" in col.lower():
            return "line"

    # Two numeric columns
    if len(numeric_cols) >= 2:
        return "scatter"

    return "table"