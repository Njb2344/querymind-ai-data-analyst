"""
main.py

Interactive interface for asking questions to the AI SQL engine.
"""

from pipelines.query_pipeline import run_question


def main():

    print("\nAI SQL Analyst Ready")
    print("--------------------")

    while True:

        question = input("\nAsk a question (or type exit): ")

        if question.lower() == "exit":
            break

        try:
            df, chart_path, insight = run_question(question)

            print("\nResults:")
            print(df)

            # -------------------------------------------------
            # Display chart location (if generated)
            # -------------------------------------------------

            if chart_path:
                print("\nChart saved at:", chart_path)

            # -------------------------------------------------
            # Display AI explanation
            # -------------------------------------------------

            print("\nAI Explanation:")
            print(insight)

        except Exception as e:
            print("\nError:", e)


if __name__ == "__main__":
    main()