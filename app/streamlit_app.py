"""
streamlit_app.py

Web interface for QueryMind AI SQL Analyst.

Features:
- Natural language question input
- SQL generation display
- Query results table
- Automatic visualization
- AI dashboard (multiple charts when possible)
- AI insights
- Suggested follow-up questions
"""

# ---------------------------------------------------
# IMPORTS
# ---------------------------------------------------

import sys
import os

# Add project root to Python path so imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd

# Query pipeline (LLM → SQL → Database)
from pipelines.query_pipeline import run_question

# Visualization utilities
from visualization.chart_selector import select_chart
from visualization.chart_generator import generate_chart
from visualization.dashboard_generator import generate_dashboard


# ---------------------------------------------------
# PAGE CONFIGURATION
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

# Initialize history if it doesn't exist
if "history" not in st.session_state:
    st.session_state.history = []


# ---------------------------------------------------
# SIDEBAR WITH EXAMPLE QUESTIONS
# ---------------------------------------------------

st.sidebar.title("Example Questions")

example_questions = [
    "Sales by state",
    "Top 10 customers by orders",
    "Orders by product category",
    "Monthly revenue"
]

for q in example_questions:
    if st.sidebar.button(q):
        st.session_state["preset_question"] = q


# ---------------------------------------------------
# CHAT INPUT
# ---------------------------------------------------

# If sidebar question was clicked
preset_question = st.session_state.get("preset_question", None)

# Chat-style input
question = st.chat_input("Ask a business question")

# If user clicked sidebar suggestion
if preset_question:
    question = preset_question
    st.session_state["preset_question"] = None


# ---------------------------------------------------
# DISPLAY PREVIOUS QUESTIONS
# ---------------------------------------------------

for item in st.session_state.history:

    with st.chat_message("user"):
        st.write(item["question"])

    with st.chat_message("assistant"):
        st.write("Analysis generated")


# ---------------------------------------------------
# MAIN QUESTION HANDLING
# ---------------------------------------------------

if question:

    # Display the user question
    with st.chat_message("user"):
        st.write(question)

    try:

        # ---------------------------------------------------
        # RUN THE FULL AI PIPELINE
        # ---------------------------------------------------

        result = run_question(question)

        df = result["dataframe"]
        sql = result["sql"]
        insight = result.get("insight", "No insight generated.")

        # Save question in session history
        st.session_state.history.append({
            "question": question
        })

        # ---------------------------------------------------
        # TWO COLUMN LAYOUT
        # ---------------------------------------------------

        # Left side → data + charts
        # Right side → AI explanation
        col1, col2 = st.columns([2, 1])


        # ---------------------------------------------------
        # LEFT COLUMN : DATA + VISUALIZATION
        # ---------------------------------------------------

        with col1:

            st.subheader("Query Results")

            # Display dataframe
            st.dataframe(df)


            # ---------------------------------------------------
            # AI DASHBOARD
            # ---------------------------------------------------

            st.subheader("AI Dashboard")

            # If enough rows exist, generate multiple charts
            if len(df) > 3:

                figures = generate_dashboard(df)

                for fig in figures:
                    st.pyplot(fig)

            else:

                # Fallback to single chart
                chart_type = select_chart(df)

                if chart_type != "table":

                    chart_path = generate_chart(df, chart_type)

                    st.image(chart_path)

                else:
                    st.info("No chart available for this result.")


        # ---------------------------------------------------
        # RIGHT COLUMN : AI ANALYST PANEL
        # ---------------------------------------------------

        with col2:

            st.subheader("AI Analyst")

            # Display generated SQL
            st.markdown("**Generated SQL**")
            st.code(sql, language="sql")

            # AI insight
            st.markdown("**Insight**")
            st.write(insight)

            # Additional analysis sections if available
            if "observation" in result:
                st.markdown("**Observation**")
                st.write(result["observation"])

            if "business_meaning" in result:
                st.markdown("**Business Meaning**")
                st.write(result["business_meaning"])


        # ---------------------------------------------------
        # SUGGESTED FOLLOW-UP QUESTIONS
        # ---------------------------------------------------

        st.subheader("Suggested Follow-up Questions")

        suggestions = [
            "Revenue trend over time",
            "Top products in the best state",
            "Orders by product category",
            "Top customers by revenue"
        ]

        cols = st.columns(len(suggestions))

        for i, q in enumerate(suggestions):
            if cols[i].button(q):
                st.session_state["preset_question"] = q
                st.experimental_rerun()


    # ---------------------------------------------------
    # ERROR HANDLING
    # ---------------------------------------------------

    except Exception as e:
        st.error(f"Error: {e}")