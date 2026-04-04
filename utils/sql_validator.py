"""
sql_validator.py

Validates SQL queries for safety before execution.

Enforces:
    - Only SELECT queries allowed
    - Dangerous keywords blocked
    - Row limits enforced
    - Query complexity checks
"""

import re
import logging
from config.settings import BLOCKED_SQL_KEYWORDS, MAX_ROWS, MAX_JOINS

logger = logging.getLogger(__name__)


def validate_sql(sql_query: str) -> str:
    """
    Validate and sanitize a SQL query for safe execution.

    Parameters
    ----------
    sql_query : str
        The SQL query to validate.

    Returns
    -------
    str
        The validated (and possibly modified) SQL query.

    Raises
    ------
    ValueError
        If the query contains blocked operations or is unsafe.
    """
    if not sql_query or not sql_query.strip():
        raise ValueError("SQL query is empty.")

    # Remove SQL comments that could hide malicious keywords
    cleaned = re.sub(r'/\*.*?\*/', ' ', sql_query, flags=re.DOTALL)
    cleaned = re.sub(r'--.*$', ' ', cleaned, flags=re.MULTILINE)

    sql_upper = cleaned.upper().strip()

    # ---------------------------------------------------
    # Rule 1: Only SELECT queries allowed
    # ---------------------------------------------------
    if not sql_upper.startswith("SELECT"):
        logger.warning("Blocked non-SELECT query: %s", sql_query[:100])
        raise ValueError("Only SELECT queries are allowed.")

    # ---------------------------------------------------
    # Rule 2: Block dangerous keywords
    # ---------------------------------------------------
    for keyword in BLOCKED_SQL_KEYWORDS:
        # Use word boundary matching to avoid false positives
        # e.g., "DELETED_AT" should not trigger "DELETE"
        pattern = r'\b' + keyword + r'\b'
        if re.search(pattern, sql_upper):
            logger.warning("Blocked keyword '%s' detected in query.", keyword)
            raise ValueError(
                f"Blocked SQL operation detected: {keyword}. "
                "Only SELECT queries are permitted."
            )

    # ---------------------------------------------------
    # Rule 3: Block multiple statements (injection)
    # ---------------------------------------------------
    # Strip trailing semicolons (LLMs often add them)
    # Then check if any remain, which would indicate multiple statements
    without_strings = re.sub(r"'[^']*'", '', cleaned)
    without_strings = without_strings.rstrip().rstrip(';').strip()
    if ';' in without_strings:
        logger.warning("Multiple SQL statements detected.")
        raise ValueError(
            "Multiple SQL statements are not allowed. "
            "Please ask one question at a time."
        )

    # ---------------------------------------------------
    # Rule 4: Check JOIN complexity
    # ---------------------------------------------------
    join_count = len(re.findall(r'\bJOIN\b', sql_upper))
    if join_count > MAX_JOINS:
        logger.warning("Query has %d JOINs (max: %d).", join_count, MAX_JOINS)
        raise ValueError(
            f"Query is too complex ({join_count} JOINs). "
            f"Maximum allowed is {MAX_JOINS}."
        )

    # ---------------------------------------------------
    # Rule 5: Clean trailing semicolons and enforce LIMIT
    # ---------------------------------------------------
    sql_query = sql_query.rstrip().rstrip(';').strip()

    if "LIMIT" not in sql_query.upper():
        sql_query = sql_query + f" LIMIT {MAX_ROWS}"
        logger.info("Added LIMIT %d to query.", MAX_ROWS)

    logger.info("SQL validation passed.")
    return sql_query
