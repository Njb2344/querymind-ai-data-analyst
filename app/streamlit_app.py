"""
streamlit_app.py

Web interface for QueryMind AI SQL Analyst.

Allows users to:
1. Ask natural language questions
2. See generated SQL
3. View query results
4. Display automatic charts

Run with:
streamlit run app/streamlit_app.py
"""

import sys
import os

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd

from pipelines.query_pipeline import run_question
from visualization.chart_selector import select_chart
from visualization.chart_generator import generate_chart


# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="QueryMind AI Analyst",
    page_icon="📊",
    layout="wide"
)

st.title("📊 QueryMind — AI Data Analyst")

st.markdown(
"""
Ask questions about your database using **natural language**.

Examples:
- Top 10 customers by orders
- Sales by state
- Monthly revenue
"""
)


# ---------------------------------------------------
# USER INPUT
# ---------------------------------------------------

question = st.text_input("Ask your question")


# ---------------------------------------------------
# RUN QUERY BUTTON
# ---------------------------------------------------

if st.button("Run Analysis"):

    if question.strip() == "":
        st.warning("Please enter a question.")
        st.stop()

    try:

        # Run the full AI pipeline
        result = run_question(question)

        df = result["dataframe"]
        sql = result["sql"]

        # -------------------------
        # Show SQL
        # -------------------------

        st.subheader("Generated SQL")

        st.code(sql, language="sql")

        # -------------------------
        # Show Data
        # -------------------------

        st.subheader("Query Results")

        st.dataframe(df)

        # -------------------------
        # Visualization
        # -------------------------

        chart_type = select_chart(df)

        if chart_type != "table":

            st.subheader("Visualization")

            chart_path = generate_chart(df, chart_type)

            st.image(chart_path)

        else:
            st.info("No chart available for this result.")

        # -------------------------
        # Insight
        # -------------------------
        st.subheader("AI Insight")
        st.write(result["insight"])

        

    except Exception as e:

        st.error(f"Error: {e}")