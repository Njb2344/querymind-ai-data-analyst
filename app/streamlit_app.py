"""
streamlit_app.py

This file implements the Streamlit web interface for QueryMind.

QueryMind is an AI-powered data analyst that allows users to:
- Ask questions in natural language
- Automatically generate SQL queries
- Execute them on a PostgreSQL database
- Visualize results
- Generate insights and reports

This module ONLY handles the UI layer.

The backend logic is handled by other modules:
    pipelines/           → query pipeline
    visualization/       → charts and dashboards
    analysis/            → EDA, query planning, reports
"""

# ---------------------------------------------------
# IMPORTS
# ---------------------------------------------------

import sys
import os

# Add project root directory to Python path
# This allows us to import modules like:
# pipelines.query_pipeline
# visualization.chart_generator
# analysis.eda_engine
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

# Streamlit is the framework used to create the web UI
import streamlit as st

# Pandas handles tabular data returned from the database
import pandas as pd


# ---------------------------------------------------
# IMPORT INTERNAL PROJECT MODULES
# ---------------------------------------------------

# Main AI pipeline
# Responsible for: question → SQL → dataframe → insight
from pipelines.query_pipeline import run_question

# Chart utilities
from visualization.chart_selector import select_chart
from visualization.chart_generator import generate_chart
from visualization.dashboard_generator import generate_dashboard

# Exploratory Data Analysis engine
from analysis.eda_engine import run_eda

# AI query planner (splits complex questions into multiple queries)
from analysis.query_planner import plan_queries

# AI report generator
from analysis.report_generator import generate_report


# ---------------------------------------------------
# STREAMLIT PAGE CONFIGURATION
# ---------------------------------------------------

# Configure browser tab title, icon, and layout
st.set_page_config(
    page_title="QueryMind AI Analyst",
    page_icon="📊",
    layout="wide"
)

# Main page title
st.title("📊 QueryMind — AI Data Analyst")

# Short subtitle explaining the tool
st.caption(
    "Natural language analytics powered by LLM + PostgreSQL"
)


# ---------------------------------------------------
# SESSION STATE INITIALIZATION
# ---------------------------------------------------


# Chat history
if "history" not in st.session_state:
    st.session_state.history = []

# Conversation memory for follow-up questions
if "conversation_context" not in st.session_state:
    st.session_state.conversation_context = []

# Preset question selected from sidebar
if "preset_question" not in st.session_state:
    st.session_state.preset_question = None


# ---------------------------------------------------
# SIDEBAR EXAMPLE QUESTIONS
# ---------------------------------------------------

st.sidebar.title("Example Questions")

example_questions = [
    "Sales by state",
    "Top 10 customers by orders",
    "Orders by product category",
    "Monthly revenue",
    "Analyze sales performance"
]

# Create a button for each example question
for q in example_questions:

    if st.sidebar.button(q):

        # Save selected question in session state
        st.session_state.preset_question = q


# ---------------------------------------------------
# USER QUESTION INPUT
# ---------------------------------------------------


# Chat input box
question = st.chat_input("Ask a business question")

# If user clicked a sidebar example
if st.session_state.preset_question:

    # Replace input question with preset question
    question = st.session_state.preset_question

    # Reset preset value
    st.session_state.preset_question = None


# ---------------------------------------------------
# DISPLAY PREVIOUS CHAT HISTORY
# ---------------------------------------------------

"""
Display previously asked questions.

Each question appears as a chat message.
"""

for item in st.session_state.history:

    with st.chat_message("user"):
        st.write(item["question"])

    with st.chat_message("assistant"):
        st.write("Analysis generated")


# ---------------------------------------------------
# HANDLE NEW USER QUESTION
# ---------------------------------------------------

if question:

    # Display user message in chat
    with st.chat_message("user"):
        st.write(question)

    try:

        # ---------------------------------------------------
        # QUERY PLANNER
        # ---------------------------------------------------

        queries = plan_queries(question)

        results = []

        # Run pipeline for each query
        for q in queries:

            result = run_question(
                q,
                context=st.session_state.conversation_context
            )

            results.append((q, result))

            # Store context for follow-up questions
            st.session_state.conversation_context.append({
                "question": q,
                "sql": result["sql"]
            })


        # ---------------------------------------------------
        # DISPLAY RESULTS
        # ---------------------------------------------------

        for q, result in results:

            df = result["dataframe"]
            sql = result["sql"]
            insight = result.get("insight", "No insight generated.")

            # Save question in chat history
            st.session_state.history.append({"question": q})

            st.divider()
            st.subheader(f"Analysis: {q}")


            # ---------------------------------------------------
            # TWO-COLUMN LAYOUT
            # ---------------------------------------------------

            """
            Left column → data and charts
            Right column → AI explanation
            """

            col1, col2 = st.columns([2, 1])


            # ---------------------------------------------------
            # LEFT COLUMN (DATA + VISUALIZATION)
            # ---------------------------------------------------

            with col1:

                # Display dataframe
                st.write("Query Results")
                st.dataframe(df)


                # ---------------------------------------------------
                # EDA MODE
                # ---------------------------------------------------

                """
                If the user asks for dataset explanation,
                run automatic exploratory data analysis.
                """

                if (
                    "explain dataset" in question.lower()
                    or "eda" in question.lower()
                ):

                    st.subheader("Dataset Analysis")

                    eda = run_eda(df)

                    # Dataset summary
                    st.write("Dataset Summary")
                    st.json(eda["summary"])

                    # Missing values
                    if not eda["missing"].empty:
                        st.write("Missing Values")
                        st.dataframe(eda["missing"])

                    # Distribution plots
                    st.write("Distributions")

                    for fig in eda["distributions"]:
                        st.pyplot(fig)

                    # Correlation heatmap
                    if eda["correlation"]:
                        st.write("Correlation Heatmap")
                        st.pyplot(eda["correlation"])

                    # Automatic insights
                    st.write("Automatic Insights")

                    for line in eda["insights"]:
                        st.write("-", line)


                # ---------------------------------------------------
                # AI DASHBOARD
                # ---------------------------------------------------

                st.subheader("Dashboard")

                if len(df) > 3:

                    # Generate multiple charts
                    figures = generate_dashboard(df)

                    for fig in figures:
                        st.pyplot(fig)

                else:

                    # Fallback single chart
                    chart_type = select_chart(df)

                    if chart_type != "table":

                        chart_path = generate_chart(df, chart_type)

                        st.image(chart_path)

                    else:
                        st.info("No chart available.")


            # ---------------------------------------------------
            # RIGHT COLUMN (AI ANALYST PANEL)
            # ---------------------------------------------------

            with col2:

                st.subheader("AI Analyst")

                # Display generated SQL query
                st.markdown("**Generated SQL**")
                st.code(sql, language="sql")

                # AI explanation
                st.markdown("**Insight**")
                st.write(insight)


            # ---------------------------------------------------
            # AI REPORT GENERATION
            # ---------------------------------------------------

            if st.button(f"Generate AI Report for: {q}"):

                report = generate_report(df, q)

                st.subheader("AI Business Report")

                st.write("Summary")
                st.write(report["summary"])

                st.write("Key Findings")
                for f in report["findings"]:
                    st.write("-", f)

                st.write("Observations")
                for o in report["observations"]:
                    st.write("-", o)

                st.write("Business Implications")
                for i in report["implications"]:
                    st.write("-", i)


        # ---------------------------------------------------
        # FOLLOW-UP QUESTIONS
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

                st.session_state.preset_question = q
                st.rerun()


    # ---------------------------------------------------
    # ERROR HANDLING
    # ---------------------------------------------------

    except Exception as e:

        st.error(f"Error: {e}")