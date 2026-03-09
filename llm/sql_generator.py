"""
sql_generator.py

Generate SQL using a local LLM (Ollama).
No API key required.
"""

import ollama

from llm.prompts import (
    PROMPT_TEMPLATE,
    SCHEMA_DESCRIPTION,
    TABLE_RELATIONSHIPS,
    SQL_RULES
)


def build_prompt(user_question: str) -> str:
    """
    Build the prompt for the LLM
    """

    prompt = PROMPT_TEMPLATE.format(
        schema=SCHEMA_DESCRIPTION,
        relationships=TABLE_RELATIONSHIPS,
        rules=SQL_RULES,
        question=user_question
    )

    return prompt


def generate_sql(user_question: str) -> str:
    """
    Generate SQL query using a local LLM
    """

    prompt = build_prompt(user_question)

    response = ollama.chat(
        model="llama3",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    sql_query = response["message"]["content"]
    
    # Remove markdown formatting if present
    sql_query = sql_query.replace("```sql", "").replace("```", "").strip()

    return sql_query