"""
query_runner.py

Executes validated SQL queries against PostgreSQL
and returns results as pandas DataFrames.
"""

import logging
import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError

from database.db_connection import get_engine
from config.settings import QUERY_TIMEOUT

logger = logging.getLogger(__name__)


def run_query(sql_query: str) -> pd.DataFrame:
    """
    Execute a SQL query and return a pandas DataFrame.

    Parameters
    ----------
    sql_query : str
        A validated SELECT query.

    Returns
    -------
    pandas.DataFrame
        Query results.

    Raises
    ------
    ValueError
        If the query is empty.
    ConnectionError
        If the database is unreachable.
    RuntimeError
        If the query fails to execute.
    """
    if not sql_query or not sql_query.strip():
        raise ValueError("Cannot execute an empty SQL query.")

    engine = get_engine()

    try:
        logger.info("Executing SQL query...")
        logger.debug("Query: %s", sql_query)

        with engine.connect() as conn:
            # Set statement timeout to prevent runaway queries
            conn.execute(
                text(f"SET statement_timeout = '{QUERY_TIMEOUT * 1000}'")
            )
            df = pd.read_sql(text(sql_query), conn)

        logger.info(
            "Query returned %d rows and %d columns.",
            df.shape[0], df.shape[1]
        )
        return df

    except ProgrammingError as e:
        logger.error("SQL syntax error: %s", e)
        raise RuntimeError(
            "The generated SQL query contains a syntax error. "
            "Please try rephrasing your question."
        ) from e

    except OperationalError as e:
        error_msg = str(e).lower()
        if "timeout" in error_msg or "cancel" in error_msg:
            logger.error("Query timed out after %ds", QUERY_TIMEOUT)
            raise RuntimeError(
                f"Query timed out after {QUERY_TIMEOUT} seconds. "
                "Try a more specific question to reduce result size."
            ) from e

        logger.error("Database error: %s", e)
        raise ConnectionError(
            "Lost connection to the database. Please check that PostgreSQL is running."
        ) from e

    except Exception as e:
        logger.error("Unexpected error executing query: %s", e)
        raise RuntimeError(
            f"An unexpected error occurred while executing the query: {e}"
        ) from e
