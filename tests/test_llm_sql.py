"""
test_llm_sql.py

This script tests the complete LLM → SQL pipeline.
"""

from pipelines.query_pipeline import run_question


def main():

    question = "Show the top 10 customers with the most orders"

    df = run_question(question)

    print("\nQuery Results:")
    print(df.head())


if __name__ == "__main__":
    main()