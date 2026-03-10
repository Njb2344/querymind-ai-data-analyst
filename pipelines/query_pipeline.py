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
from llm.explanation import generate_explanation
from visualization.chart_selector import select_chart
from visualization.chart_generator import generate_chart


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

    # -------------------------------------------------
    # Step 4 — Decide which chart to create
    # -------------------------------------------------

    chart_type = select_chart(df)

    print("\nSelected chart type:", chart_type)

    # -------------------------------------------------
    # Step 5 — Generate visualization
    # -------------------------------------------------

    chart_path = generate_chart(df, chart_type)

    if chart_path:
        print("\nChart generated at:", chart_path)

    # -------------------------------------------------
    # Step 6 — Generate insight
    # -------------------------------------------------
    insight = generate_explanation(question, df)

    print(insight)

    return {
        "sql": sql_query,
        "dataframe": df, 
        "chart_path": chart_path,
        "insight": insight
    }