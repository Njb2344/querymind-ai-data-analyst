"""
explanation.py

Generate analytical insights from SQL query results
using a local LLM (Ollama).
"""

import logging
import ollama
import pandas as pd

from config.settings import LLM_MODEL, LLM_PREVIEW_ROWS

logger = logging.getLogger(__name__)


def dataframe_to_prompt_data(df: pd.DataFrame) -> str:
    """
    Convert dataframe into a compact text representation
    suitable for an LLM prompt.
    """
    if df.empty:
        return "The query returned no results."

    preview = df.head(LLM_PREVIEW_ROWS).to_string(index=False)

    try:
        summary = df.describe(include="all").to_string()
    except Exception as e:
        logger.warning("Could not generate summary statistics: %s", e)
        summary = "Summary statistics not available."

    return f"""
Dataset preview ({min(len(df), LLM_PREVIEW_ROWS)} of {len(df)} rows):
{preview}

Dataset summary:
{summary}
"""


def build_explanation_prompt(user_question: str, df: pd.DataFrame) -> str:
    """Build the explanation prompt."""
    data_section = dataframe_to_prompt_data(df)

    prompt = f"""
You are a senior business data analyst.

A user asked the following question:

{user_question}

The database returned the following dataset.

{data_section}

Your task is to analyze the results and explain the key insights.

Focus on:
- patterns
- rankings
- comparisons
- anomalies
- business meaning

Return the answer in this structure:

Insight:
Explain the main takeaway.

Observation:
Highlight important comparisons or patterns.

Business Meaning:
Explain why this matters.
"""
    return prompt


def generate_explanation(user_question: str, df: pd.DataFrame) -> str:
    """
    Generate an insight explanation using the LLM.

    Parameters
    ----------
    user_question : str
        The original user question.
    df : pandas.DataFrame
        Query results.

    Returns
    -------
    str
        AI-generated explanation of the results.
    """
    if df.empty:
        return "No results to analyze. The query returned an empty dataset."

    prompt = build_explanation_prompt(user_question, df)

    try:
        logger.info("Generating AI explanation...")

        response = ollama.chat(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )

        explanation = response["message"]["content"].strip()
        logger.info("Explanation generated successfully.")
        return explanation

    except Exception as e:
        logger.error("Failed to generate explanation: %s", e)
        return (
            "Could not generate AI insights at this time. "
            "Please check that Ollama is running."
        )


def generate_followup_suggestions(
    user_question: str,
    df: pd.DataFrame,
    context: list = None
) -> list:
    """
    Generate context-aware follow-up question suggestions using the LLM.

    Parameters
    ----------
    user_question : str
        The question that was just asked.
    df : pandas.DataFrame
        The results that were returned.
    context : list, optional
        Previous conversation context.

    Returns
    -------
    list[str]
        A list of 4 suggested follow-up questions.
    """
    columns = ", ".join(df.columns.tolist()) if not df.empty else "none"
    row_count = len(df)

    context_text = ""
    if context:
        recent = context[-3:]
        context_text = "\n".join(
            f"- {item['question']}" for item in recent
        )

    prompt = f"""
You are a data analyst assistant.

The user just asked: "{user_question}"
The result has {row_count} rows with columns: {columns}

Previous questions asked:
{context_text if context_text else "None"}

Suggest exactly 4 natural follow-up questions that would help
the user dig deeper into this data. The questions should be:
- Short (under 8 words each)
- Different from questions already asked
- Relevant to the current results and database schema

Return ONLY the 4 questions, one per line, with no numbering or bullets.
"""

    try:
        response = ollama.chat(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )

        text = response["message"]["content"].strip()
        suggestions = [
            line.strip().lstrip("0123456789.-) ")
            for line in text.split("\n")
            if line.strip() and len(line.strip()) > 5
        ][:4]

        if len(suggestions) >= 2:
            return suggestions

    except Exception as e:
        logger.warning("Failed to generate follow-up suggestions: %s", e)

    # Fallback to smart defaults based on data columns
    fallbacks = []
    if "state" in columns.lower():
        fallbacks.append("Revenue trend over time")
    if "revenue" in columns.lower() or "price" in columns.lower():
        fallbacks.append("Top products by revenue")
    if "category" in columns.lower():
        fallbacks.append("Revenue by product category")

    fallbacks.extend([
        "Monthly revenue trend",
        "Top 10 customers by orders",
        "Orders by product category",
        "Sales by state"
    ])

    return fallbacks[:4]
