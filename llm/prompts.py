"""
prompts.py

This file contains all prompt templates used by the LLM
to translate natural language questions into SQL queries.

The prompt includes:
- Database schema description
- Table relationships
- SQL generation rules
"""

# -----------------------------------------------------
# DATABASE SCHEMA DESCRIPTION
# -----------------------------------------------------

SCHEMA_DESCRIPTION = """
You are working with a PostgreSQL database.

Tables:

customers
---------
customer_id (primary key)
customer_unique_id
customer_city
customer_state


orders
------
order_id (primary key)
customer_id (foreign key -> customers.customer_id)
order_status
order_purchase_timestamp
order_delivered_customer_date


order_items
-----------
order_id (foreign key -> orders.order_id)
product_id
price
freight_value


products
--------
product_id (primary key)
product_category_name
"""


# -----------------------------------------------------
# TABLE RELATIONSHIPS
# -----------------------------------------------------

TABLE_RELATIONSHIPS = """
Relationships between tables:

orders.customer_id → customers.customer_id
order_items.order_id → orders.order_id
order_items.product_id → products.product_id
"""


# -----------------------------------------------------
# SQL GENERATION RULES
# -----------------------------------------------------

SQL_RULES = """
Rules for SQL generation:

1. Only generate SELECT queries.
2. Do NOT generate DELETE, UPDATE, INSERT, DROP, or ALTER.
3. Always use proper JOIN conditions when querying multiple tables.
4. Use LIMIT 100 when the query could return many rows.
5. The database is PostgreSQL.
6. Return ONLY the SQL query.
7. Do not include explanations or comments.
"""


# -----------------------------------------------------
# FINAL PROMPT TEMPLATE
# -----------------------------------------------------

PROMPT_TEMPLATE = """
You are an expert PostgreSQL data analyst.

Your task is to convert a user question into a valid SQL query.

DATABASE SCHEMA
----------------
{schema}

TABLE RELATIONSHIPS
-------------------
{relationships}

SQL RULES
---------
{rules}

USER QUESTION
-------------
{question}

Return ONLY the SQL query.
"""