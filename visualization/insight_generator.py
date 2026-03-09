"""

This module extracts simple insights from the dataframe
to provide a human-readable explanation of the results.
"""


def generate_insight(df):
    """
    Generate a simple analytical insight from the dataframe.

    Parameters
    ----------
    df : pandas.DataFrame

    Returns
    -------
    str
        Generated insight
    """

    # If dataframe does not have two columns,
    # insight generation becomes ambiguous
    if df.shape[1] != 2:
        return "Insight generation not available for this result."

    # Extract column names
    category_column = df.columns[0]
    metric_column = df.columns[1]

    # Find row with maximum metric value
    max_row = df.loc[df[metric_column].idxmax()]

    # Extract category and metric values
    category_value = max_row[category_column]
    metric_value = max_row[metric_column]

    # Generate textual insight
    insight = (
        f"{category_value} has the highest {metric_column} "
        f"with a value of {metric_value}."
    )

    return insight