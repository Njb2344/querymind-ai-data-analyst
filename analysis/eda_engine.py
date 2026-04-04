"""
eda_engine.py

Automatic Exploratory Data Analysis (EDA) engine for QueryMind.

Purpose
-------
This module performs automatic analysis of a dataframe returned
from the database or query pipeline.

It generates:

1) Dataset summary
2) Missing value analysis
3) Distribution plots for numeric columns
4) Correlation heatmap for numeric features
5) Basic automatic insights

This allows QueryMind to automatically explain datasets
without requiring manual exploration from the user.
"""

# ---------------------------------------------------
# IMPORTS
# ---------------------------------------------------

# Pandas for dataframe manipulation
import pandas as pd

# Matplotlib for plotting figures
import matplotlib.pyplot as plt

# Seaborn for statistical visualizations
import seaborn as sns


# ---------------------------------------------------
# DATASET SUMMARY
# ---------------------------------------------------

def dataset_summary(df):
    """
    Generate basic structural information about the dataset.

    Parameters
    ----------
    df : pandas.DataFrame
        The dataframe to analyze.

    Returns
    -------
    dict
        Dictionary containing:
        - number of rows
        - number of columns
        - number of numeric columns
        - number of categorical columns
    """

    summary = {

        # Total number of rows
        "rows": df.shape[0],

        # Total number of columns
        "columns": df.shape[1],

        # Count numeric columns
        "numeric_columns": len(
            df.select_dtypes(include="number").columns
        ),

        # Count categorical columns
        "categorical_columns": len(
            df.select_dtypes(include="object").columns
        )
    }

    return summary


# ---------------------------------------------------
# MISSING VALUE ANALYSIS
# ---------------------------------------------------

def missing_values(df):
    """
    Analyze missing values in the dataset.

    Parameters
    ----------
    df : pandas.DataFrame

    Returns
    -------
    pandas.DataFrame
        Table containing:
        - column name
        - number of missing values
        - percentage of missing values
    """

    # Count missing values per column
    missing = df.isnull().sum()

    # Convert results into a dataframe
    missing_df = pd.DataFrame({

        # Column names
        "column": missing.index,

        # Missing value counts
        "missing_count": missing.values,

        # Percentage of missing values
        "missing_percentage": (missing.values / len(df)) * 100
    })

    # Keep only columns that actually contain missing values
    missing_df = missing_df[
        missing_df["missing_count"] > 0
    ]

    return missing_df


# ---------------------------------------------------
# NUMERIC DISTRIBUTION PLOTS
# ---------------------------------------------------

def numeric_distributions(df):
    """
    Generate histogram distributions for numeric columns.

    These plots help understand the shape of the data
    (normal, skewed, heavy tail, etc).

    Parameters
    ----------
    df : pandas.DataFrame

    Returns
    -------
    list
        List of matplotlib figures.
    """

    figures = []

    # Select numeric columns only
    numeric_cols = df.select_dtypes(include="number").columns

    # Create a histogram for each numeric column
    for col in numeric_cols:

        fig, ax = plt.subplots()

        sns.histplot(
            df[col],
            kde=True,     # Add density curve
            ax=ax
        )

        ax.set_title(f"Distribution of {col}")

        figures.append(fig)

    return figures


# ---------------------------------------------------
# CORRELATION HEATMAP
# ---------------------------------------------------

def correlation_heatmap(df):
    """
    Generate correlation matrix visualization.

    Shows relationships between numeric variables.

    Parameters
    ----------
    df : pandas.DataFrame

    Returns
    -------
    matplotlib.figure or None
    """

    # Select numeric columns
    numeric_df = df.select_dtypes(include="number")

    # If fewer than 2 numeric columns exist,
    # correlation cannot be computed
    if numeric_df.shape[1] < 2:
        return None

    # Compute correlation matrix
    corr = numeric_df.corr()

    # Create heatmap figure
    fig, ax = plt.subplots(figsize=(6, 4))

    sns.heatmap(
        corr,
        annot=True,        # display correlation values
        cmap="coolwarm",
        ax=ax
    )

    ax.set_title("Correlation Heatmap")

    return fig


# ---------------------------------------------------
# AUTOMATIC INSIGHT GENERATION
# ---------------------------------------------------

def generate_insights(df):
    """
    Generate simple automated insights based on dataset statistics.

    These insights are heuristic-based (not LLM generated).
    They give quick interpretations of the data.

    Parameters
    ----------
    df : pandas.DataFrame

    Returns
    -------
    list
        List of insight strings
    """

    insights = []

    numeric_cols = df.select_dtypes(include="number").columns
    categorical_cols = df.select_dtypes(include="object").columns


    # ---------------------------------------------------
    # Most frequent categorical value
    # ---------------------------------------------------

    if len(categorical_cols) > 0:

        col = categorical_cols[0]

        # Find most frequent category
        top_value = df[col].value_counts().idxmax()

        insights.append(
            f"The most frequent value in '{col}' is '{top_value}'."
        )


    # ---------------------------------------------------
    # Numeric average insight
    # ---------------------------------------------------

    if len(numeric_cols) > 0:

        col = numeric_cols[0]

        mean_val = df[col].mean()

        insights.append(
            f"The average value of '{col}' is {mean_val:.2f}."
        )


    # ---------------------------------------------------
    # Dataset size insight
    # ---------------------------------------------------

    insights.append(
        f"The dataset contains {df.shape[0]} rows "
        f"and {df.shape[1]} columns."
    )

    return insights


# ---------------------------------------------------
# MAIN EDA PIPELINE
# ---------------------------------------------------

def run_eda(df):
    """
    Execute the full EDA analysis pipeline.

    This function orchestrates all EDA steps
    and returns a structured result dictionary.

    Parameters
    ----------
    df : pandas.DataFrame

    Returns
    -------
    dict
        Contains:
        - dataset summary
        - missing value table
        - distribution figures
        - correlation heatmap
        - generated insights
    """

    results = {}

    # Dataset structural summary
    results["summary"] = dataset_summary(df)

    # Missing value analysis
    results["missing"] = missing_values(df)

    # Numeric distributions
    results["distributions"] = numeric_distributions(df)

    # Correlation heatmap
    results["correlation"] = correlation_heatmap(df)

    # Automatic insights
    results["insights"] = generate_insights(df)

    return results