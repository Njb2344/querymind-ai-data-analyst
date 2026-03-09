"""
explanation.py

Generate analytical insights from SQL query results
using a local LLM (Ollama).
"""

import ollama
import pandas as pd


def dataframe_to_prompt_data(df: pd.DataFrame) -> str:
    """
    Convert dataframe into a compact text representation
    suitable for an LLM prompt
    """

    if df.empty:
        return "The query returned no results."

    preview = df.head(10).to_string(index=False)

    try:
        summary = df.describe(include="all").to_string()
    except:
        summary = "Summary statistics not available."

    return f"""
Dataset preview:
{preview}

Dataset summary:
{summary}
"""


def build_explanation_prompt(user_question: str, df: pd.DataFrame) -> str:
    """
    Build the explanation prompt
    """

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
    Generate an insight explanation using the LLM
    """

    prompt = build_explanation_prompt(user_question, df)

    response = ollama.chat(
        model="llama3",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    explanation = response["message"]["content"]

    return explanation.strip()