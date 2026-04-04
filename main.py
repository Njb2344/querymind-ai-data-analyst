"""
main.py

Interactive CLI interface for asking questions to the AI SQL engine.
"""

import logging
from config.settings import LOG_LEVEL, LOG_FORMAT
from pipelines.query_pipeline import run_question

# Configure logging
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


def main():

    print("\n" + "=" * 50)
    print("  QueryMind - AI SQL Analyst")
    print("=" * 50)
    print("Ask questions in natural language.")
    print("Type 'exit' to quit.\n")

    context = []

    while True:

        question = input("\nYour question: ").strip()

        if not question:
            print("Please enter a question.")
            continue

        if question.lower() in ("exit", "quit", "q"):
            print("\nGoodbye!")
            break

        try:
            result = run_question(question, context=context)

            df = result["dataframe"]
            sql = result["sql"]
            chart_path = result["chart_path"]
            insight = result["insight"]

            # Store context for follow-ups
            context.append({"question": question, "sql": sql})

            # Display results
            print("\n--- Generated SQL ---")
            print(sql)

            print(f"\n--- Results ({len(df)} rows) ---")
            print(df.to_string())

            if chart_path:
                print(f"\nChart saved: {chart_path}")

            print("\n--- AI Insight ---")
            print(insight)

        except ConnectionError as e:
            print(f"\nConnection Error: {e}")
            print("Please check that Ollama and PostgreSQL are running.")

        except ValueError as e:
            print(f"\nValidation Error: {e}")

        except RuntimeError as e:
            print(f"\nRuntime Error: {e}")

        except Exception as e:
            logger.exception("Unexpected error:")
            print(f"\nUnexpected Error: {e}")


if __name__ == "__main__":
    main()
