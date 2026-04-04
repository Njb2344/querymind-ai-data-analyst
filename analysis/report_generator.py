"""
report_generator.py

Generates AI-style business reports from query results.

Produces structured insights with:
    - Summary
    - Key findings (data-driven)
    - Observations (data-driven)
    - Business implications (data-driven)
"""

import logging
import pandas as pd
import ollama

from config.settings import LLM_MODEL, LLM_PREVIEW_ROWS

logger = logging.getLogger(__name__)


def generate_report(df: pd.DataFrame, question: str) -> dict:
    """
    Generate a structured analytical report.

    Uses a combination of heuristic analysis and LLM-generated
    insights for data-driven observations.

    Parameters
    ----------
    df : pandas.DataFrame
        The dataframe returned from the SQL query.
    question : str
        The original user question.

    Returns
    -------
    dict
        {
            "summary": str,
            "findings": list[str],
            "observations": list[str],
            "implications": list[str]
        }
    """
    report = {}

    # ---------------------------------------------------
    # Section 1 - Summary
    # ---------------------------------------------------
    report["summary"] = (
        f"The query '{question}' returned a dataset "
        f"containing {df.shape[0]} rows and {df.shape[1]} columns."
    )

    # ---------------------------------------------------
    # Section 2 - Key Findings (data-driven)
    # ---------------------------------------------------
    findings = []

    numeric_cols = df.select_dtypes(include="number").columns
    categorical_cols = df.select_dtypes(include="object").columns

    if len(numeric_cols) > 0 and len(categorical_cols) > 0:
        try:
            top_row = df.sort_values(
                numeric_cols[0], ascending=False
            ).iloc[0]
            bottom_row = df.sort_values(
                numeric_cols[0], ascending=True
            ).iloc[0]

            findings.append(
                f"The top performing '{categorical_cols[0]}' "
                f"is '{top_row[categorical_cols[0]]}' "
                f"with {numeric_cols[0]} = {top_row[numeric_cols[0]]:.2f}."
            )
            findings.append(
                f"The lowest performing '{categorical_cols[0]}' "
                f"is '{bottom_row[categorical_cols[0]]}' "
                f"with {numeric_cols[0]} = {bottom_row[numeric_cols[0]]:.2f}."
            )
        except Exception as e:
            logger.warning("Could not compute top/bottom findings: %s", e)

    if len(numeric_cols) > 0:
        col = numeric_cols[0]
        avg_val = df[col].mean()
        std_val = df[col].std()
        median_val = df[col].median()

        findings.append(
            f"Average {col}: {avg_val:.2f} | "
            f"Median: {median_val:.2f} | "
            f"Std Dev: {std_val:.2f}"
        )

        # Concentration analysis
        if len(df) >= 5:
            top_5_share = (
                df[col].nlargest(5).sum() / df[col].sum() * 100
                if df[col].sum() > 0 else 0
            )
            findings.append(
                f"Top 5 entries account for {top_5_share:.1f}% of total {col}."
            )

    report["findings"] = findings

    # ---------------------------------------------------
    # Section 3 - Observations (LLM-generated)
    # ---------------------------------------------------
    report["observations"] = _generate_llm_observations(df, question)

    # ---------------------------------------------------
    # Section 4 - Business Implications (LLM-generated)
    # ---------------------------------------------------
    report["implications"] = _generate_llm_implications(df, question)

    return report


def _generate_llm_observations(df: pd.DataFrame, question: str) -> list:
    """Generate data-driven observations using the LLM."""
    preview = df.head(LLM_PREVIEW_ROWS).to_string(index=False)

    prompt = f"""
You are a data analyst. Based on this dataset for the question "{question}":

{preview}

Write exactly 3 specific, data-driven observations.
Each observation must reference actual values from the data.
Return ONLY the 3 observations, one per line, no numbering.
"""

    try:
        response = ollama.chat(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        lines = [
            line.strip().lstrip("0123456789.-) ")
            for line in response["message"]["content"].strip().split("\n")
            if line.strip() and len(line.strip()) > 10
        ]
        if len(lines) >= 2:
            return lines[:3]

    except Exception as e:
        logger.warning("LLM observation generation failed: %s", e)

    # Fallback to heuristic observations
    observations = []
    numeric_cols = df.select_dtypes(include="number").columns

    if len(numeric_cols) > 0:
        col = numeric_cols[0]
        if df[col].std() > df[col].mean() * 0.5:
            observations.append(
                f"High variability detected in {col} "
                f"(coefficient of variation: {df[col].std() / df[col].mean():.1%})."
            )
        else:
            observations.append(
                f"Values in {col} are relatively consistent "
                f"(std dev: {df[col].std():.2f})."
            )

    observations.append(
        f"The dataset contains {df.shape[0]} entries across {df.shape[1]} dimensions."
    )

    return observations


def _generate_llm_implications(df: pd.DataFrame, question: str) -> list:
    """Generate business implications using the LLM."""
    preview = df.head(LLM_PREVIEW_ROWS).to_string(index=False)

    prompt = f"""
You are a business strategist. Based on this data for "{question}":

{preview}

Write exactly 3 actionable business implications.
Each must be specific to this data, not generic advice.
Return ONLY the 3 implications, one per line, no numbering.
"""

    try:
        response = ollama.chat(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        lines = [
            line.strip().lstrip("0123456789.-) ")
            for line in response["message"]["content"].strip().split("\n")
            if line.strip() and len(line.strip()) > 10
        ]
        if len(lines) >= 2:
            return lines[:3]

    except Exception as e:
        logger.warning("LLM implication generation failed: %s", e)

    # Fallback
    return [
        "Review top-performing segments for investment opportunities.",
        "Investigate underperforming areas for potential improvements.",
    ]
