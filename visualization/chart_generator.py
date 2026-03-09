"""

This module generates charts using matplotlib and seaborn.

Input:
    - dataframe
    - chart type

Output:
    - saved chart image
"""

import os
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path


# Directory where charts will be stored
OUTPUT_DIR = Path("outputs/charts") 

def get_next_chart_path():
    """
    Generate the next chart filename automatically.

    Example output:
    chart_001.png
    chart_002.png
    chart_003.png
    """

    # Ensure directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Get all existing chart files
    existing = list(OUTPUT_DIR.glob("chart_*.png"))

    if not existing:
        next_id = 1
    else:
        # Extract numeric IDs
        ids = [int(f.stem.split("_")[1]) for f in existing]
        next_id = max(ids) + 1

    filename = f"chart_{next_id:03d}.png"

    return OUTPUT_DIR / filename


def generate_chart(df, chart_type):
    """
    Generate a chart from dataframe results.

    Parameters
    ----------
    df : pandas.DataFrame
        Query result dataframe

    chart_type : str
        Type of chart to generate

    Returns
    -------
    str
        Path of saved chart image
    """

    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Define output file path
    chart_path = get_next_chart_path()
    print("Saving chart to:", chart_path)

    # Create figure canvas
    plt.figure(figsize=(8, 5))

    # BAR CHART
    if chart_type == "bar":

        # Detect numeric column automatically
        numeric_col = df.select_dtypes(include="number").columns[0]

        # Detect categorical column
        categorical_col = df.select_dtypes(include="object").columns[0]

        # x-axis: first column
        # y-axis: second column
        sns.barplot(
            x=df[categorical_col],
            y=df[numeric_col]
        )

        plt.xlabel(categorical_col)
        plt.ylabel(numeric_col)
        plt.title("Bar Chart Visualization")
        plt.title(f"{numeric_col} by {categorical_col}")

    # LINE CHART
    elif chart_type == "line":

        numeric_col = df.select_dtypes(include="number").columns[0]

        sns.lineplot(
            x=df.index,
            y=df[numeric_col]
        )

        plt.title("Trend Over Time")

    # SCATTER PLOT
    elif chart_type == "scatter":

        numeric_cols = df.select_dtypes(include="number").columns[:2]

        sns.scatterplot(
            x=df[numeric_cols[0]],
            y=df[numeric_cols[1]]
        )

        plt.title("Relationship Between Variables")

    else:
        # If no valid chart type, return None
        return None

    # Rotate x-axis labels if needed
    plt.xticks(rotation=45)

    # Adjust layout to avoid label clipping
    plt.tight_layout()

    # Save chart image
    plt.savefig(chart_path)

    # Close figure to free memory
    plt.close()

    return str(chart_path)