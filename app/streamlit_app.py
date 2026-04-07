"""
streamlit_app.py

Streamlit web interface for QueryMind — AI Data Analyst.
Dark professional theme with polished layout.
"""

# ---------------------------------------------------
# IMPORTS
# ---------------------------------------------------

import sys
import os
import io
import time
import logging

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from config.settings import LOG_LEVEL, LOG_FORMAT

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

from pipelines.query_pipeline import run_question
from visualization.chart_selector import select_chart
from visualization.chart_generator import generate_chart
from visualization.dashboard_generator import generate_dashboard
from analysis.eda_engine import run_eda
from analysis.query_planner import plan_queries
from analysis.report_generator import generate_report
from llm.explanation import generate_followup_suggestions


# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="QueryMind AI Analyst",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ---------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------

st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .main-header {
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 4px;
    }
    .main-header h1 {
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        background: linear-gradient(135deg, #4F8BF9 0%, #636EFA 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .subtitle {
        color: #8B8FA3;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #1A1D23;
        border: 1px solid #2A2D35;
        border-radius: 10px;
        padding: 18px 20px;
        margin-bottom: 12px;
    }
    .metric-card h4 {
        color: #8B8FA3;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin: 0 0 6px 0;
    }
    .metric-card .value {
        color: #FAFAFA;
        font-size: 1.4rem;
        font-weight: 600;
    }
    .insight-card {
        background: #1A1D23;
        border: 1px solid #2A2D35;
        border-radius: 10px;
        padding: 20px 22px;
        margin: 10px 0;
        line-height: 1.7;
    }
    .section-label {
        color: #4F8BF9;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin: 20px 0 8px 0;
    }
    section[data-testid="stSidebar"] {
        background: #12141A;
        border-right: 1px solid #1E2028;
    }
    section[data-testid="stSidebar"] .stButton > button {
        width: 100%;
        text-align: left;
        background: #1A1D23;
        border: 1px solid #2A2D35;
        color: #C8CCD8;
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 0.85rem;
        transition: all 0.2s;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: #22252D;
        border-color: #4F8BF9;
        color: #FAFAFA;
    }
    .stDownloadButton > button {
        background: transparent;
        border: 1px solid #2A2D35;
        color: #8B8FA3;
        border-radius: 8px;
        font-size: 0.8rem;
        padding: 6px 16px;
        transition: all 0.2s;
    }
    .stDownloadButton > button:hover {
        border-color: #4F8BF9;
        color: #4F8BF9;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background: #1A1D23;
        border: 1px solid #2A2D35;
        border-radius: 8px 8px 0 0;
        color: #8B8FA3;
        padding: 10px 20px;
        font-size: 0.85rem;
    }
    .stTabs [aria-selected="true"] {
        background: #22252D;
        border-color: #4F8BF9;
        color: #FAFAFA;
    }
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
    }
    hr {
        border-color: #1E2028;
    }
    .stChatMessage {
        background: #1A1D23;
        border: 1px solid #2A2D35;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------
# HEADER
# ---------------------------------------------------

st.markdown("""
<div class="main-header">
    <span style="font-size: 2.2rem;">📊</span>
    <h1>QueryMind</h1>
</div>
<div class="subtitle">AI-powered data analytics — ask questions, get insights</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------
# SESSION STATE
# ---------------------------------------------------

if "history" not in st.session_state:
    st.session_state.history = []
if "conversation_context" not in st.session_state:
    st.session_state.conversation_context = []
if "preset_question" not in st.session_state:
    st.session_state.preset_question = None
if "last_suggestions" not in st.session_state:
    st.session_state.last_suggestions = []
if "last_results" not in st.session_state:
    st.session_state.last_results = []
if "last_question" not in st.session_state:
    st.session_state.last_question = None


# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

with st.sidebar:
    st.markdown("### Quick Questions")
    st.caption("Click to run a pre-built analysis")

    example_questions = [
        ("📈", "Sales by state"),
        ("👥", "Top 10 customers by orders"),
        ("📦", "Orders by product category"),
        ("💰", "Monthly revenue"),
        ("🔍", "Analyze sales performance"),
    ]

    for icon, q in example_questions:
        if st.button(f"{icon}  {q}", key=f"sidebar_{q}"):
            st.session_state.preset_question = q

    st.markdown("---")
    total_queries = len(st.session_state.history)
    st.caption(f"Queries this session: **{total_queries}**")

    st.markdown("---")
    st.markdown(
        '<p style="color:#555; font-size:0.75rem;">'
        'QueryMind v1.0<br>Llama3 + PostgreSQL</p>',
        unsafe_allow_html=True
    )


# ---------------------------------------------------
# USER INPUT
# ---------------------------------------------------

question = st.chat_input("Ask a business question...")

if st.session_state.preset_question:
    question = st.session_state.preset_question
    st.session_state.preset_question = None


# ---------------------------------------------------
# CHAT HISTORY (previous queries only)
# ---------------------------------------------------

for item in st.session_state.history:
    with st.chat_message("user"):
        st.write(item["question"])
    with st.chat_message("assistant"):
        st.write("Analysis complete")


# ---------------------------------------------------
# RUN NEW QUERY (only when a new question is asked)
# ---------------------------------------------------

if question:
    with st.chat_message("user"):
        st.write(question)

    try:
        with st.spinner("Planning analysis..."):
            queries = plan_queries(question)

        results = []
        for q in queries:
            with st.spinner(f"Analyzing: {q}..."):
                start_time = time.time()
                result = run_question(
                    q, context=st.session_state.conversation_context
                )
                elapsed = time.time() - start_time
                result["elapsed"] = elapsed
                results.append((q, result))

                st.session_state.conversation_context.append({
                    "question": q,
                    "sql": result["sql"]
                })

        # Persist results and question in session state
        st.session_state.last_results = [
            (q, {
                "sql": r["sql"],
                "dataframe": r["dataframe"],
                "chart_path": r.get("chart_path"),
                "insight": r.get("insight", ""),
                "elapsed": r.get("elapsed", 0),
            })
            for q, r in results
        ]
        st.session_state.last_question = question

        # Add to history
        for q, _ in results:
            st.session_state.history.append({"question": q})

        # Generate follow-up suggestions
        if results:
            last_q, last_result = results[-1]
            last_df = last_result["dataframe"]
            with st.spinner("Generating suggestions..."):
                st.session_state.last_suggestions = generate_followup_suggestions(
                    last_q, last_df,
                    context=st.session_state.conversation_context
                )

    except ConnectionError as e:
        st.error(f"**Connection Error:** {e}")
        st.info("Make sure Ollama and PostgreSQL are running.")

    except ValueError as e:
        st.warning(f"**Validation Error:** {e}")

    except RuntimeError as e:
        st.error(f"**Error:** {e}")

    except Exception as e:
        logger.exception("Unexpected error:")
        st.error(f"An unexpected error occurred: {e}")


# ---------------------------------------------------
# DISPLAY RESULTS (persisted — survives reruns)
# ---------------------------------------------------

if st.session_state.last_results:

    for q, result in st.session_state.last_results:

        df = result["dataframe"]
        sql = result["sql"]
        insight = result.get("insight", "No insight generated.")
        elapsed = result.get("elapsed", 0)

        # --- Quick metrics ---
        st.markdown(
            f'<div class="section-label">Analysis: {q}</div>',
            unsafe_allow_html=True
        )

        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(
                f'<div class="metric-card">'
                f'<h4>Rows</h4>'
                f'<div class="value">{len(df):,}</div></div>',
                unsafe_allow_html=True
            )
        with m2:
            st.markdown(
                f'<div class="metric-card">'
                f'<h4>Columns</h4>'
                f'<div class="value">{len(df.columns)}</div></div>',
                unsafe_allow_html=True
            )
        with m3:
            st.markdown(
                f'<div class="metric-card">'
                f'<h4>Query Time</h4>'
                f'<div class="value">{elapsed:.1f}s</div></div>',
                unsafe_allow_html=True
            )

        # --- Tabs ---
        tab_data, tab_charts, tab_insight, tab_sql = st.tabs(
            ["📋 Data", "📊 Charts", "💡 Insights", "🔧 SQL"]
        )

        # --- TAB: Data ---
        with tab_data:
            st.dataframe(df, use_container_width=True, height=400)

            col_csv, col_space = st.columns([1, 3])
            with col_csv:
                st.download_button(
                    label="Download CSV",
                    data=df.to_csv(index=False),
                    file_name="querymind_results.csv",
                    mime="text/csv",
                    key=f"csv_{q}"
                )

            # EDA mode
            if st.session_state.last_question and (
                "explain dataset" in st.session_state.last_question.lower()
                or "eda" in st.session_state.last_question.lower()
            ):
                st.markdown(
                    '<div class="section-label">Exploratory Analysis</div>',
                    unsafe_allow_html=True
                )
                with st.spinner("Running EDA..."):
                    eda = run_eda(df)

                st.json(eda["summary"])

                if not eda["missing"].empty:
                    st.write("**Missing Values**")
                    st.dataframe(eda["missing"])

                for fig in eda["distributions"]:
                    st.pyplot(fig)
                    plt.close(fig)

                if eda["correlation"]:
                    st.pyplot(eda["correlation"])
                    plt.close(eda["correlation"])

                for line in eda["insights"]:
                    st.write(f"- {line}")

        # --- TAB: Charts ---
        with tab_charts:
            if len(df) > 3:
                figures = generate_dashboard(df)

                for i, fig in enumerate(figures):
                    st.pyplot(fig)

                    buf = io.BytesIO()
                    fig.savefig(
                        buf, format="png", dpi=150,
                        bbox_inches="tight", facecolor="#0E1117"
                    )
                    buf.seek(0)
                    st.download_button(
                        label=f"Download Chart {i + 1}",
                        data=buf,
                        file_name=f"chart_{i + 1}.png",
                        mime="image/png",
                        key=f"chart_{q}_{i}"
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

        # --- TAB: Insights ---
        with tab_insight:
            st.markdown(
                f'<div class="insight-card">{insight}</div>',
                unsafe_allow_html=True
            )

            if st.button("Generate Full Report", key=f"report_{q}"):
                with st.spinner("Generating report..."):
                    report = generate_report(df, q)

                st.markdown(
                    '<div class="section-label">Summary</div>',
                    unsafe_allow_html=True
                )
                st.write(report["summary"])

                st.markdown(
                    '<div class="section-label">Key Findings</div>',
                    unsafe_allow_html=True
                )
                for f in report["findings"]:
                    st.write(f"- {f}")

                st.markdown(
                    '<div class="section-label">Observations</div>',
                    unsafe_allow_html=True
                )
                for o in report["observations"]:
                    st.write(f"- {o}")

                st.markdown(
                    '<div class="section-label">Business Implications</div>',
                    unsafe_allow_html=True
                )
                for imp in report["implications"]:
                    st.write(f"- {imp}")

        # --- TAB: SQL ---
        with tab_sql:
            st.markdown(
                '<div class="section-label">Generated Query</div>',
                unsafe_allow_html=True
            )
            st.code(sql, language="sql")

    # --- Follow-up suggestions ---
    st.markdown("---")
    st.markdown(
        '<div class="section-label">Suggested Follow-ups</div>',
        unsafe_allow_html=True
    )

    suggestions = st.session_state.last_suggestions
    if suggestions:
        cols = st.columns(min(len(suggestions), 4))
        for i, s in enumerate(suggestions):
            if cols[i].button(s, key=f"followup_{s}"):
                st.session_state.preset_question = s
                st.rerun()
