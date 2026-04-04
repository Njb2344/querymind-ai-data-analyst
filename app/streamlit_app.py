"""
streamlit_app.py

Streamlit web interface for QueryMind.

QueryMind is an AI-powered data analyst that allows users to:
- Ask questions in natural language
- Automatically generate SQL queries
- Execute them on a PostgreSQL database
- Visualize results with charts and dashboards
- Generate insights and reports
- Export results as CSV or charts

This module ONLY handles the UI layer.
"""

# ---------------------------------------------------
# IMPORTS
# ---------------------------------------------------

import sys
import os
import io
import logging

# Add project root directory to Python path
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from config.settings import LOG_LEVEL, LOG_FORMAT

# Configure logging
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

# ---------------------------------------------------
# IMPORT INTERNAL PROJECT MODULES
# ---------------------------------------------------

from pipelines.query_pipeline import run_question
from visualization.chart_selector import select_chart
from visualization.chart_generator import generate_chart
from visualization.dashboard_generator import generate_dashboard
from analysis.eda_engine import run_eda
from analysis.query_planner import plan_queries
from analysis.report_generator import generate_report
from llm.explanation import generate_followup_suggestions


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
# SESSION STATE INITIALIZATION
# ---------------------------------------------------

if "history" not in st.session_state:
    st.session_state.history = []

if "conversation_context" not in st.session_state:
    st.session_state.conversation_context = []

if "preset_question" not in st.session_state:
    st.session_state.preset_question = None

if "last_suggestions" not in st.session_state:
    st.session_state.last_suggestions = []


# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

st.sidebar.title("Example Questions")

example_questions = [
    "Sales by state",
    "Top 10 customers by orders",
    "Orders by product category",
    "Monthly revenue",
    "Analyze sales performance"
]

for q in example_questions:
    if st.sidebar.button(q, key=f"sidebar_{q}"):
        st.session_state.preset_question = q

st.sidebar.divider()
st.sidebar.caption("QueryMind v1.0")
st.sidebar.caption("Powered by Llama3 + PostgreSQL")


# ---------------------------------------------------
# USER INPUT
# ---------------------------------------------------

question = st.chat_input("Ask a business question...")

if st.session_state.preset_question:
    question = st.session_state.preset_question
    st.session_state.preset_question = None


# ---------------------------------------------------
# DISPLAY CHAT HISTORY
# ---------------------------------------------------

for item in st.session_state.history:
    with st.chat_message("user"):
        st.write(item["question"])
    with st.chat_message("assistant"):
        st.write("Analysis generated")


# ---------------------------------------------------
# HANDLE NEW QUESTION
# ---------------------------------------------------

if question:

    with st.chat_message("user"):
        st.write(question)

    try:
        # ---------------------------------------------------
        # QUERY PLANNER
        # ---------------------------------------------------

        with st.spinner("Planning analysis..."):
            queries = plan_queries(question)

        results = []

        for q in queries:
            with st.spinner(f"Analyzing: {q}..."):
                result = run_question(
                    q,
                    context=st.session_state.conversation_context
                )
                results.append((q, result))

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

            st.session_state.history.append({"question": q})

            st.divider()
            st.subheader(f"Analysis: {q}")

            col1, col2 = st.columns([2, 1])

            # ---------------------------------------------------
            # LEFT COLUMN (DATA + VISUALIZATION)
            # ---------------------------------------------------

            with col1:

                # Dataframe display
                st.write("**Query Results**")
                st.dataframe(df, use_container_width=True)

                # ---------------------------------------------------
                # EXPORT: CSV Download
                # ---------------------------------------------------

                csv_data = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name=f"querymind_results.csv",
                    mime="text/csv",
                    key=f"csv_{q}_{len(st.session_state.history)}"
                )

                # ---------------------------------------------------
                # EDA MODE
                # ---------------------------------------------------

                if (
                    "explain dataset" in question.lower()
                    or "eda" in question.lower()
                ):
                    st.subheader("Dataset Analysis")

                    with st.spinner("Running exploratory analysis..."):
                        eda = run_eda(df)

                    st.write("**Dataset Summary**")
                    st.json(eda["summary"])

                    if not eda["missing"].empty:
                        st.write("**Missing Values**")
                        st.dataframe(eda["missing"])

                    st.write("**Distributions**")
                    for fig in eda["distributions"]:
                        st.pyplot(fig)
                        plt.close(fig)

                    if eda["correlation"]:
                        st.write("**Correlation Heatmap**")
                        st.pyplot(eda["correlation"])
                        plt.close(eda["correlation"])

                    st.write("**Automatic Insights**")
                    for line in eda["insights"]:
                        st.write(f"- {line}")

                # ---------------------------------------------------
                # DASHBOARD
                # ---------------------------------------------------

                st.subheader("Dashboard")

                if len(df) > 3:
                    with st.spinner("Generating dashboard..."):
                        figures = generate_dashboard(df)

                    for i, fig in enumerate(figures):
                        st.pyplot(fig)

                        # Export: Chart Download
                        buf = io.BytesIO()
                        fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
                        buf.seek(0)

                        st.download_button(
                            label=f"Download Chart {i + 1}",
                            data=buf,
                            file_name=f"chart_{i + 1}.png",
                            mime="image/png",
                            key=f"chart_{q}_{i}_{len(st.session_state.history)}"
                        )

                        plt.close(fig)

                else:
                    chart_type = select_chart(df)
                    if chart_type != "table":
                        chart_path = generate_chart(df, chart_type)
                        if chart_path:
                            st.image(chart_path)
                    else:
                        st.info("Not enough data for chart visualization.")

            # ---------------------------------------------------
            # RIGHT COLUMN (AI ANALYST PANEL)
            # ---------------------------------------------------

            with col2:

                st.subheader("AI Analyst")

                st.markdown("**Generated SQL**")
                st.code(sql, language="sql")

                st.markdown("**Insight**")
                st.write(insight)

            # ---------------------------------------------------
            # AI REPORT
            # ---------------------------------------------------

            if st.button(
                f"Generate AI Report",
                key=f"report_{q}_{len(st.session_state.history)}"
            ):
                with st.spinner("Generating AI report..."):
                    report = generate_report(df, q)

                st.subheader("AI Business Report")

                st.write("**Summary**")
                st.write(report["summary"])

                st.write("**Key Findings**")
                for f in report["findings"]:
                    st.write(f"- {f}")

                st.write("**Observations**")
                for o in report["observations"]:
                    st.write(f"- {o}")

                st.write("**Business Implications**")
                for imp in report["implications"]:
                    st.write(f"- {imp}")


        # ---------------------------------------------------
        # FOLLOW-UP SUGGESTIONS (LLM-generated)
        # ---------------------------------------------------

        st.subheader("Suggested Follow-up Questions")

        # Use last result for context-aware suggestions
        if results:
            last_q, last_result = results[-1]
            last_df = last_result["dataframe"]

            with st.spinner("Generating suggestions..."):
                suggestions = generate_followup_suggestions(
                    last_q,
                    last_df,
                    context=st.session_state.conversation_context
                )
                st.session_state.last_suggestions = suggestions
        else:
            suggestions = st.session_state.last_suggestions

        if suggestions:
            cols = st.columns(min(len(suggestions), 4))
            for i, s in enumerate(suggestions):
                if cols[i].button(
                    s,
                    key=f"followup_{s}_{len(st.session_state.history)}"
                ):
                    st.session_state.preset_question = s
                    st.rerun()


    # ---------------------------------------------------
    # ERROR HANDLING
    # ---------------------------------------------------

    except ConnectionError as e:
        st.error(f"Connection Error: {e}")
        st.info(
            "Please make sure Ollama and PostgreSQL are running."
        )

    except ValueError as e:
        st.warning(f"Validation Error: {e}")

    except RuntimeError as e:
        st.error(f"Error: {e}")

    except Exception as e:
        logger.exception("Unexpected error in Streamlit app:")
        st.error(
            f"An unexpected error occurred: {e}\n\n"
            "Please try again or rephrase your question."
        )
