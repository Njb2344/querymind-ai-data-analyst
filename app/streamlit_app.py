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
st.caption("Natural language analytics powered by LLM + PostgreSQL")

# ---------------------------------------------------
# SESSION STATE (CHAT HISTORY)
# ---------------------------------------------------

if "history" not in st.session_state:
    st.session_state.history = []

# ---------------------------------------------------
# Display chat history
# ---------------------------------------------------

for item in st.session_state.history:
    with st.chat_message("user"):
        st.write(item["question"])

    with st.chat_message("assistant"):
        st.write("Analysis generated")

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

question = st.chat_input("Ask a business question")


# ---------------------------------------------------
# RUN QUERY BUTTON
# ---------------------------------------------------

if question:

    if question.strip() == "":
        st.warning("Please enter a question.")
        st.stop()

    try:

        # Run the full AI pipeline
        result = run_question(question)

        df = result["dataframe"]
        sql = result["sql"]

        # Save the question in history
        st.session_state.history.append({
            "question": question
        })

        # -------------------------
        # Show SQL
        # -------------------------

        st.subheader("Generated SQL")

        st.code(sql, language="sql")

        # -------------------------
        # Show Data
        # -------------------------

        col1, col2 = st.columns([2,1])

        # Show results and chart in left column
        # Left Column → Results + Chart

        with col1:

            # -------------------------
            # Show Data
            # -------------------------
            st.subheader("Query Results")
            st.dataframe(df)

            # -------------------------
            # visualization
            # -------------------------

            chart_type = select_chart(df)

            if chart_type != "table":

                st.subheader("Visualization")

                chart_path = generate_chart(df, chart_type)

                st.image(chart_path)

            else:
                st.info("No chart available for this result.")

        # Show insight in right column
        # Right Column → Insight

        with col2:

            # -------------------------
            # Insight
            # -------------------------
            st.subheader("AI Analyst")

            st.markdown("**Generated SQL**")
            st.code(sql, language="sql")

            st.markdown("**Insight**")
            st.write(result.get("insight", "No insight generated"))    

    except Exception as e:

        st.error(f"Error: {e}")