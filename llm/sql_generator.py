"""
sql_generator.py

Generate SQL using a local LLM (Ollama).
No API key required.

This module converts a natural language question into
a PostgreSQL SQL query.

The process:

User Question
      ↓
Prompt Construction
      ↓
Local LLM (Ollama + Llama3)
      ↓
Raw LLM Response
      ↓
SQL Cleaning
      ↓
Final SQL Query
"""

# ---------------------------------------------------
# IMPORTS
# ---------------------------------------------------

# Ollama allows us to run local LLMs such as Llama3
import ollama

# Prompt components
# These contain database schema, relationships, and rules
from llm.prompts import (
    PROMPT_TEMPLATE,
    SCHEMA_DESCRIPTION,
    TABLE_RELATIONSHIPS,
    SQL_RULES
)


# ---------------------------------------------------
# PROMPT BUILDER
# ---------------------------------------------------

def build_prompt(user_question: str, context: str = "") -> str:
    """
    Build the prompt that will be sent to the LLM.

    The prompt contains:
        • Database schema
        • Table relationships
        • SQL rules
        • Conversation context (optional)
        • The user's question

    Parameters
    ----------
    user_question : str
        Natural language question asked by the user.

    context : str
        Previous conversation context.
        This helps the LLM understand follow-up questions.

    Returns
    -------
    str
        Fully constructed prompt to send to the LLM.
    """

    # Combine context with the question if context exists
    if context:
        user_question = f"""
Previous conversation context:
{context}

Current user question:
{user_question}
"""

    # Format the main prompt template
    prompt = PROMPT_TEMPLATE.format(
        schema=SCHEMA_DESCRIPTION,
        relationships=TABLE_RELATIONSHIPS,
        rules=SQL_RULES,
        question=user_question
    )

    return prompt


# ---------------------------------------------------
# SQL GENERATION FUNCTION
# ---------------------------------------------------

def generate_sql(user_question: str, context: str = "") -> str:
    """
    Generate SQL query using a local LLM (Llama3 via Ollama).

    Parameters
    ----------
    user_question : str
        Natural language question asked by the user.

    context : str
        Previous conversation context used for follow-up queries.

    Returns
    -------
    str
        Clean SQL query ready to execute.
    """

    # ---------------------------------------------------
    # STEP 1 — BUILD PROMPT
    # ---------------------------------------------------

    prompt = build_prompt(user_question, context)


    # ---------------------------------------------------
    # STEP 2 — CALL LOCAL LLM
    # ---------------------------------------------------

    response = ollama.chat(
        model="llama3",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )


    # ---------------------------------------------------
    # STEP 3 — EXTRACT LLM OUTPUT
    # ---------------------------------------------------

    sql_query = response["message"]["content"]


    # ---------------------------------------------------
    # STEP 4 — CLEAN MARKDOWN FORMATTING
    # ---------------------------------------------------

    # Sometimes LLM outputs SQL like:
    #
    # ```sql
    # SELECT ...
    # ```
    #
    # We remove the markdown formatting.

    sql_query = (
        sql_query
        .replace("```sql", "")
        .replace("```", "")
        .strip()
    )


    # ---------------------------------------------------
    # STEP 5 — REMOVE EXTRA TEXT
    # ---------------------------------------------------

    # LLMs sometimes generate text like:
    #
    # "Here is the SQL query:"
    #
    # We detect where SELECT starts and keep only SQL.

    if "SELECT" in sql_query.upper():

        sql_query = sql_query[
            sql_query.upper().find("SELECT") :
        ]


    # ---------------------------------------------------
    # STEP 6 — RETURN FINAL SQL
    # ---------------------------------------------------

    return sql_query