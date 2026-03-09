"""
query_pipeline.py

This module orchestrates the full query process:

User Question
      ↓
Generate SQL using LLM
      ↓
Validate SQL for safety
      ↓
Execute query on PostgreSQL
      ↓
Return results as pandas DataFrame
"""

# Import modules
from llm.sql_generator import generate_sql
from utils.sql_validator import validate_sql
from database.query_runner import run_query


def run_question(question: str):
    """
    Run a full natural language query pipeline.

    Parameters
    ----------
    question : str
        User natural language question

    Returns
    -------
    pandas.DataFrame
        Query results
    """

    print("\nUser Question:")
    print(question)

    # -------------------------------------------------
    # Step 1 — Generate SQL from LLM
    # -------------------------------------------------

    sql_query = generate_sql(question)

    print("\nGenerated SQL:")
    print(sql_query)

    # -------------------------------------------------
    # Step 2 — Validate SQL safety
    # -------------------------------------------------

    if not validate_sql(sql_query):
        raise ValueError("Unsafe SQL detected. Query blocked.")

    # -------------------------------------------------
    # Step 3 — Execute SQL
    # -------------------------------------------------

    df = run_query(sql_query)

    print("\nQuery executed successfully.")

    return df