"""
QueryMind — Data Ingestion Script

Purpose:
--------
This script loads the Olist e-commerce dataset (CSV files) into the
PostgreSQL database used by the QueryMind project.

Pipeline:
---------
CSV files  →  Pandas DataFrames  →  PostgreSQL Tables

Why this is necessary:
----------------------
The dataset originally exists as CSV files. However, QueryMind's AI
needs a relational SQL database to run analytical queries.

Therefore, this script converts the raw dataset into a structured
PostgreSQL database.
"""

# ===============================
# 1. IMPORT REQUIRED LIBRARIES
# ===============================

import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path


# ===============================
# 2. DATABASE CONNECTION CONFIG
# ===============================

"""
These variables define how Python connects to PostgreSQL.

Change DB_PASSWORD to match your PostgreSQL password.
"""

DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "querymind_db"

"""
SQLAlchemy creates a connection engine that allows Python
to interact with the PostgreSQL database.
"""

engine = create_engine(
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


# ===============================
# 3. DEFINE DATASET LOCATION
# ===============================

"""
The dataset CSV files were placed earlier in:

QueryMind/data/raw/

Pathlib makes file paths OS-independent.
"""

DATA_PATH = Path("../data/raw")


# ===============================
# 4. LOAD THE CSV FILES
# ===============================

"""
Each CSV file corresponds to a table in the Olist dataset.

We load them into Pandas DataFrames so we can clean and
prepare the data before inserting it into PostgreSQL.
"""

customers = pd.read_csv(DATA_PATH / "olist_customers_dataset.csv")
orders = pd.read_csv(DATA_PATH / "olist_orders_dataset.csv")
order_items = pd.read_csv(DATA_PATH / "olist_order_items_dataset.csv")
products = pd.read_csv(DATA_PATH / "olist_products_dataset.csv")
payments = pd.read_csv(DATA_PATH / "olist_order_payments_dataset.csv")
sellers = pd.read_csv(DATA_PATH / "olist_sellers_dataset.csv")


# ===============================
# 5. SELECT ONLY NECESSARY COLUMNS
# ===============================

"""
The raw dataset contains many columns that are not needed
for our analytical database.

Selecting only relevant columns improves:

- database performance
- SQL query clarity
- LLM SQL generation reliability
"""

customers = customers[
    ["customer_id", "customer_unique_id", "customer_city", "customer_state"]
]

orders = orders[
    [
        "order_id",
        "customer_id",
        "order_status",
        "order_purchase_timestamp",
        "order_delivered_customer_date",
    ]
]

products = products[
    [
        "product_id",
        "product_category_name",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    ]
]

order_items = order_items[
    ["order_id", "product_id", "seller_id", "price", "freight_value"]
]

payments = payments[
    ["order_id", "payment_type", "payment_installments", "payment_value"]
]

sellers = sellers[
    ["seller_id", "seller_city", "seller_state"]
]


# ===============================
# 6. INSERT DATA INTO POSTGRESQL
# ===============================

"""
Pandas provides the .to_sql() method to insert DataFrames
directly into SQL tables.

Arguments explanation:

table_name     → target PostgreSQL table
engine         → database connection
if_exists      → "append" means add rows to existing table
index=False    → do not insert the Pandas index as a column
"""

customers.to_sql("customers", engine, if_exists="append", index=False)

orders.to_sql("orders", engine, if_exists="append", index=False)

products.to_sql("products", engine, if_exists="append", index=False)

sellers.to_sql("sellers", engine, if_exists="append", index=False)

order_items.to_sql("order_items", engine, if_exists="append", index=False)

payments.to_sql("payments", engine, if_exists="append", index=False)


# ===============================
# 7. CONFIRM DATA LOADING
# ===============================

print("===================================")
print("QueryMind Data Ingestion Complete")
print("All dataset tables loaded successfully.")
print("===================================")