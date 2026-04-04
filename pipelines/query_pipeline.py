"""
query_pipeline.py

Orchestrates the full query process:

    User Question
          |
    Generate SQL using LLM
          |
    Validate SQL for safety
          |
    Execute query on PostgreSQL
          |
    Generate chart + insights
          |
    Return structured results
"""

import logging

from llm.sql_generator import generate_sql
from utils.sql_validator import validate_sql
from database.query_runner import run_query
from llm.explanation import generate_explanation
from visualization.chart_selector import select_chart
from visualization.chart_generator import generate_chart
from config.settings import MAX_CONTEXT_HISTORY

logger = logging.getLogger(__name__)


def run_question(question: str, context: list = None) -> dict:
    """
    Run a full natural language query pipeline.

    Parameters
    ----------
    question : str
        User natural language question.
    context : list, optional
        List of previous question/sql dicts for conversation memory.

    Returns
    -------
    dict
        {
            "sql": str,
            "dataframe": pandas.DataFrame,
            "chart_path": str or None,
            "insight": str
        }

    Raises
    ------
    ConnectionError
        If Ollama or database is unreachable.
    ValueError
        If the generated SQL is unsafe.
    RuntimeError
        If the query fails at any step.
    """
    logger.info("Processing question: %s", question)

    # -------------------------------------------------
    # Step 0 - Build context for LLM
    # -------------------------------------------------
    history_text = ""

    if context:
        recent_context = context[-MAX_CONTEXT_HISTORY:]
        for item in recent_context:
            history_text += (
                f"\nPrevious Question: {item['question']}\n"
                f"SQL Used: {item['sql']}\n"
            )

    # -------------------------------------------------
    # Step 1 - Generate SQL from LLM
    # -------------------------------------------------
    logger.info("Step 1: Generating SQL...")
    sql_query = generate_sql(question, history_text)

    # -------------------------------------------------
    # Step 2 - Validate SQL safety
    # -------------------------------------------------
    logger.info("Step 2: Validating SQL...")
    sql_query = validate_sql(sql_query)

    # -------------------------------------------------
    # Step 3 - Execute SQL
    # -------------------------------------------------
    logger.info("Step 3: Executing query...")
    df = run_query(sql_query)

    # -------------------------------------------------
    # Step 4 - Select chart type
    # -------------------------------------------------
    logger.info("Step 4: Selecting chart type...")
    chart_type = select_chart(df)

    # -------------------------------------------------
    # Step 5 - Generate visualization
    # -------------------------------------------------
    logger.info("Step 5: Generating visualization...")
    chart_path = None
    if chart_type != "table":
        chart_path = generate_chart(df, chart_type)

    # -------------------------------------------------
    # Step 6 - Generate insight
    # -------------------------------------------------
    logger.info("Step 6: Generating insights...")
    insight = generate_explanation(question, df)

    logger.info("Pipeline completed successfully.")

    return {
        "sql": sql_query,
        "dataframe": df,
        "chart_path": chart_path,
        "insight": insight
    }
