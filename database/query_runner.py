import pandas as pd
from database.db_connection import get_engine
from utils.sql_validator import validate_sql


def run_query(sql_query):

    # validate SQL first
    validate_sql(sql_query)

    engine = get_engine()

    df = pd.read_sql(sql_query, engine)

    return df