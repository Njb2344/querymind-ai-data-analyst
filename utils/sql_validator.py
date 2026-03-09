def validate_sql(sql_query):

    blocked_keywords = [
        "DELETE",
        "DROP",
        "UPDATE",
        "INSERT",
        "ALTER",
        "TRUNCATE" 
    ]

    sql_upper = sql_query.upper()

    for keyword in blocked_keywords:
        if keyword in sql_upper:
            raise ValueError(
                f"Blocked SQL operation detected: {keyword}"
            )

    if not sql_upper.strip().startswith("SELECT"):
        raise ValueError("Only SELECT queries are allowed")
    
    # If no rule was violated, the query is safe
    return True