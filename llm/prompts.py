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
order_item_id
product_id
price
freight_value


products
--------
product_id (primary key)
product_category_name
"""

# -----------------------------------------------------
# DATASET RULES
# -----------------------------------------------------

DATASET_RULES = """
Dataset Rules:

1. The table order_items does NOT contain a quantity column.
2. Each row in order_items represents ONE purchased item.
3. Therefore sales must be calculated as:

SUM(order_items.price)

4. To compute total revenue, always use SUM(price).
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
Rules for generating SQL:

- Only use the tables provided in the schema.
- Never invent columns.
- Never use a column named quantity.
- Always aggregate revenue using SUM(order_items.price).
- Always use GROUP BY when aggregating.
- Prefer clear aliases for tables:
    customers -> c
    orders -> o
    order_items -> oi
    products -> p
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