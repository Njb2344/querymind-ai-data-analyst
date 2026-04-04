"""
settings.py

Centralized configuration for the QueryMind application.

All configurable values are defined here to avoid
hardcoded values scattered across the codebase.
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ---------------------------------------------------
# DATABASE CONFIGURATION
# ---------------------------------------------------

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "querymind_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")


# ---------------------------------------------------
# LLM CONFIGURATION
# ---------------------------------------------------

LLM_MODEL = os.getenv("LLM_MODEL", "llama3")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")


# ---------------------------------------------------
# SQL GUARDRAILS
# ---------------------------------------------------

# Maximum number of rows a query can return
MAX_ROWS = int(os.getenv("MAX_ROWS", "10000"))

# Query execution timeout in seconds
QUERY_TIMEOUT = int(os.getenv("QUERY_TIMEOUT", "30"))

# Maximum number of JOINs allowed in a single query
MAX_JOINS = int(os.getenv("MAX_JOINS", "5"))

# Blocked SQL keywords (unsafe operations)
BLOCKED_SQL_KEYWORDS = [
    "DELETE", "DROP", "UPDATE", "INSERT", "ALTER",
    "TRUNCATE", "GRANT", "REVOKE", "COPY",
]


# ---------------------------------------------------
# VISUALIZATION
# ---------------------------------------------------

CHART_FIGSIZE = (8, 5)
DASHBOARD_FIGSIZE = (6, 4)
CHART_OUTPUT_DIR = "outputs/charts"
CHART_DPI = 150


# ---------------------------------------------------
# CONVERSATION
# ---------------------------------------------------

# Number of previous queries to include as context
MAX_CONTEXT_HISTORY = 3

# Maximum rows to show in LLM data preview
LLM_PREVIEW_ROWS = 10


# ---------------------------------------------------
# LOGGING
# ---------------------------------------------------

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
