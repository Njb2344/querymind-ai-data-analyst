"""
report_generator.py

This module generates **AI-style business reports**
based on query results.

Purpose
-------
A traditional data analyst does not only provide
tables and charts.

They also produce structured insights such as:

    • Summary
    • Key findings
    • Observations
    • Business implications

This module converts a dataframe into a simple
business-style analytical report.

It is NOT an LLM module — it uses heuristic logic
based on the dataframe contents.
"""

import pandas as pd


# ---------------------------------------------------
# MAIN REPORT GENERATION FUNCTION
# ---------------------------------------------------

def generate_report(df, question):
    """
    Generate a structured analytical report.

    Parameters
    ----------
    df : pandas.DataFrame
        The dataframe returned from the SQL query.

    question : str
        The original user question.

    Returns
    -------
    dict
        Dictionary containing structured report sections:

        {
            "summary": str,
            "findings": list[str],
            "observations": list[str],
            "implications": list[str]
        }
    """

    # Initialize report structure
    report = {}

    # ---------------------------------------------------
    # SECTION 1 — SUMMARY
    # ---------------------------------------------------

    # Describe the size and structure of the dataset
    report["summary"] = (
        f"The query '{question}' returned a dataset "
        f"containing {df.shape[0]} rows and {df.shape[1]} columns."
    )


    # ---------------------------------------------------
    # SECTION 2 — KEY FINDINGS
    # ---------------------------------------------------

    findings = []

    # Detect numeric and categorical columns
    numeric_cols = df.select_dtypes(include="number").columns
    categorical_cols = df.select_dtypes(include="object").columns

    # If both numeric and categorical columns exist,
    # we can determine top-performing entities
    if len(numeric_cols) > 0 and len(categorical_cols) > 0:

        # Sort dataset by first numeric column
        top_row = df.sort_values(
            numeric_cols[0],
            ascending=False
        ).iloc[0]

        findings.append(
            f"The top performing '{categorical_cols[0]}' "
            f"is '{top_row[categorical_cols[0]]}'."
        )

    # If numeric columns exist,
    # compute average metric
    if len(numeric_cols) > 0:

        avg_value = df[numeric_cols[0]].mean()

        findings.append(
            f"The average value of '{numeric_cols[0]}' "
            f"is {avg_value:.2f}."
        )

    report["findings"] = findings


    # ---------------------------------------------------
    # SECTION 3 — OBSERVATIONS
    # ---------------------------------------------------

    report["observations"] = [

        # Generic analytical observation
        "The dataset shows variation across categories.",

        # Suggest concentration effect
        "Performance appears concentrated among top entries."
    ]


    # ---------------------------------------------------
    # SECTION 4 — BUSINESS IMPLICATIONS
    # ---------------------------------------------------

    report["implications"] = [

        # Strategic insight
        "Focus business strategy on top-performing segments.",

        # Growth recommendation
        "Investigate underperforming segments for growth opportunities."
    ]


    # ---------------------------------------------------
    # RETURN FINAL REPORT
    # ---------------------------------------------------

    return report