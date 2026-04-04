"""
sql_generator.py

Generate SQL using a local LLM (Ollama).

This module converts a natural language question into
a PostgreSQL SQL query.

The process:

    User Question
          |
    Prompt Construction
          |
    Local LLM (Ollama + Llama3)
          |
    Raw LLM Response
          |
    SQL Cleaning
          |
    Final SQL Query
"""

import logging
import ollama

from llm.prompts import (
    PROMPT_TEMPLATE,
    SCHEMA_DESCRIPTION,
    TABLE_RELATIONSHIPS,
    SQL_RULES
)
from config.settings import LLM_MODEL

logger = logging.getLogger(__name__)


def build_prompt(user_question: str, context: str = "") -> str:
    """
    Build the prompt that will be sent to the LLM.

    Parameters
    ----------
    user_question : str
        Natural language question asked by the user.
    context : str
        Previous conversation context.

    Returns
    -------
    str
        Fully constructed prompt to send to the LLM.
    """
    if context:
        user_question = f"""
Previous conversation context:
{context}

Current user question:
{user_question}
"""

    prompt = PROMPT_TEMPLATE.format(
        schema=SCHEMA_DESCRIPTION,
        relationships=TABLE_RELATIONSHIPS,
        rules=SQL_RULES,
        question=user_question
    )

    return prompt


def generate_sql(user_question: str, context: str = "") -> str:
    """
    Generate SQL query using a local LLM (Llama3 via Ollama).

    Parameters
    ----------
    user_question : str
        Natural language question asked by the user.
    context : str
        Previous conversation context.

    Returns
    -------
    str
        Clean SQL query ready to execute.

    Raises
    ------
    ConnectionError
        If Ollama service is not running.
    RuntimeError
        If the LLM fails to generate valid SQL.
    """
    prompt = build_prompt(user_question, context)

    # Call local LLM with retry logic
    max_retries = 2

    for attempt in range(max_retries + 1):
        try:
            logger.info(
                "Calling LLM (%s) for SQL generation (attempt %d)...",
                LLM_MODEL, attempt + 1
            )

            response = ollama.chat(
                model=LLM_MODEL,
                messages=[{"role": "user", "content": prompt}]
            )

            sql_query = response["message"]["content"]
            break

        except Exception as e:
            if "connection" in str(e).lower() or "refused" in str(e).lower():
                logger.error("Cannot connect to Ollama: %s", e)
                raise ConnectionError(
                    "Cannot connect to Ollama. Please make sure Ollama is "
                    "running with: ollama serve"
                ) from e

            if attempt < max_retries:
                logger.warning(
                    "LLM call failed (attempt %d): %s. Retrying...",
                    attempt + 1, e
                )
                continue

            logger.error("LLM failed after %d attempts: %s", max_retries + 1, e)
            raise RuntimeError(
                "The AI model failed to generate a SQL query. "
                "Please try again or rephrase your question."
            ) from e

    # Clean markdown formatting
    sql_query = (
        sql_query
        .replace("```sql", "")
        .replace("```", "")
        .strip()
    )

    # Remove extra text before SELECT
    if "SELECT" in sql_query.upper():
        sql_query = sql_query[sql_query.upper().find("SELECT"):]
    else:
        logger.warning("LLM response does not contain SELECT: %s", sql_query[:200])
        raise RuntimeError(
            "The AI model did not generate a valid SQL query. "
            "Please try rephrasing your question."
        )

    logger.info("SQL generated successfully.")
    logger.debug("Generated SQL: %s", sql_query)

    return sql_query
