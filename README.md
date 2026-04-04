# QueryMind — AI Data Analyst

QueryMind is an AI-powered data analytics system that lets users query databases using natural language. It automatically converts questions into SQL, executes them, generates visualizations, and provides business insights — all through an interactive web interface.

## What It Does

- Converts natural language questions into optimized PostgreSQL queries
- Executes queries against a real database and returns structured results
- Automatically selects and generates the best chart type for the data
- Produces AI-generated business insights and reports
- Splits complex questions into multiple analytical queries
- Provides context-aware follow-up suggestions
- Supports exploratory data analysis (EDA) on any result set

## Architecture

```
User Question (Natural Language)
        │
        ▼
┌──────────────────┐
│  Streamlit UI    │  ← Web interface with chat, charts, exports
└──────────────────┘
        │
        ▼
┌──────────────────┐
│  Query Planner   │  ← Splits complex questions into sub-queries
└──────────────────┘
        │
        ▼
┌──────────────────┐
│ Query Pipeline   │  ← Orchestrates the full workflow
└──────────────────┘
        │
   ┌────┼─────┬──────────┐
   ▼    ▼     ▼          ▼
 SQL  SQL   Database  Visualization
 Gen  Valid  Exec     + Insights
```

**Key modules:**

- `llm/` — SQL generation and insight explanation via Ollama (Llama3)
- `database/` — PostgreSQL connection, query execution, schema
- `pipelines/` — Main orchestrator connecting all components
- `visualization/` — Chart selection, generation, and dashboards
- `analysis/` — EDA engine, query planner, report generator
- `utils/` — SQL validation and safety guardrails
- `config/` — Centralized configuration
- `app/` — Streamlit web interface

## Tech Stack

- **Python** — Core language
- **Ollama + Llama3** — Local LLM (no API costs)
- **PostgreSQL** — Relational database
- **Streamlit** — Web UI framework
- **Pandas** — Data manipulation
- **Matplotlib + Seaborn** — Visualization
- **SQLAlchemy** — Database ORM

## Database

The project uses the Olist e-commerce dataset with 6 tables: `customers`, `orders`, `order_items`, `products`, `sellers`, and `payments`. Sales are calculated as `SUM(order_items.price)` since each row represents one purchased item (no quantity column).

## Setup

### Prerequisites

- Python 3.10+
- PostgreSQL running locally
- Ollama installed with Llama3 model

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/QueryMind.git
cd QueryMind

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Pull the LLM model
ollama pull llama3
```

### Database Setup

```bash
# Create the database
psql -U postgres -c "CREATE DATABASE querymind_db;"

# Create tables
psql -U postgres -d querymind_db -f database/schema.sql

# Load data
python database/load_data.py
```

### Configuration

Edit `.env` and update values if needed:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=querymind_db
DB_USER=postgres
DB_PASSWORD=postgres
LLM_MODEL=llama3
```

### Run

```bash
# Web interface
streamlit run app/streamlit_app.py

# CLI interface
python main.py
```

## Example Questions

- "Sales by state"
- "Top 10 customers by orders"
- "Monthly revenue"
- "Orders by product category"
- "Analyze sales performance" (triggers multi-query analysis)

## Features

### SQL Safety Guardrails

All generated SQL is validated before execution: only SELECT queries are allowed, dangerous keywords (DELETE, DROP, etc.) are blocked, row limits are enforced, query timeouts prevent runaway queries, and JOIN complexity is checked.

### Smart Query Planning

Complex questions like "Analyze sales performance" are automatically split into multiple focused queries (sales by state, monthly revenue, top categories, top customers) that together provide a comprehensive analysis.

### Export

Results can be downloaded as CSV files, and dashboard charts can be saved as PNG images directly from the web interface.

### AI Reports

Each analysis can generate a structured business report with summary, key findings, observations, and business implications — all driven by the actual data.

## Project Structure

```
QueryMind/
├── app/streamlit_app.py         # Web interface
├── main.py                      # CLI entry point
├── config/settings.py           # Centralized configuration
├── database/
│   ├── db_connection.py         # PostgreSQL connection
│   ├── query_runner.py          # Query execution
│   ├── schema.sql               # Table definitions
│   └── load_data.py             # Data ingestion
├── llm/
│   ├── sql_generator.py         # NL → SQL conversion
│   ├── explanation.py           # AI insights + follow-ups
│   └── prompts.py               # Prompt templates
├── pipelines/
│   └── query_pipeline.py        # Main orchestrator
├── visualization/
│   ├── chart_selector.py        # Auto chart type selection
│   ├── chart_generator.py       # Chart rendering
│   ├── dashboard_generator.py   # Multi-chart dashboards
│   └── insight_generator.py     # Simple data insights
├── analysis/
│   ├── eda_engine.py            # Exploratory data analysis
│   ├── query_planner.py         # Multi-query planning
│   └── report_generator.py      # Business reports
├── utils/
│   └── sql_validator.py         # SQL safety validation
├── requirements.txt
├── .env
└── README.md
```
