"""
query_planner.py

This module implements the **AI Query Planner** for QueryMind.

Purpose
-------
Not every user question should produce only ONE SQL query.

Example:

User question:
    "Analyze sales performance"

A human data analyst would typically perform multiple analyses:

    1) Sales by state
    2) Monthly revenue trend
    3) Top product categories
    4) Top customers

The Query Planner replicates this behavior by converting
a complex business question into multiple analytical queries.

Each query is then sent to the main pipeline:

    Natural Language → SQL → Database → Visualization → Insight

This module only decides **WHAT questions should be asked**.
It does NOT run SQL itself.
"""


# ---------------------------------------------------
# MAIN QUERY PLANNING FUNCTION
# ---------------------------------------------------

def plan_queries(question):
    """
    Determine whether a user question should produce
    one query or multiple analytical queries.

    Parameters
    ----------
    question : str
        Natural language question from the user.

    Returns
    -------
    list[str]
        A list of analytical questions to execute.

    Examples
    --------
    Input:
        "Analyze sales performance"

    Output:
        [
            "Sales by state",
            "Monthly revenue",
            "Top product categories",
            "Top customers by revenue"
        ]
    """

    # ---------------------------------------------------
    # Normalize the question
    # ---------------------------------------------------

    # Convert to lowercase to make keyword matching easier
    q = question.lower()


    # ---------------------------------------------------
    # Rule 1 — Sales performance analysis
    # ---------------------------------------------------

    if "sales performance" in q or "analyze sales" in q:

        # Return multiple analytical queries
        return [

            # Geographic performance
            "Sales by state",

            # Time trend
            "Monthly revenue",

            # Product segmentation
            "Top product categories",

            # Customer segmentation
            "Top customers by revenue"
        ]


    # ---------------------------------------------------
    # Rule 2 — Revenue analysis
    # ---------------------------------------------------

    if "revenue analysis" in q or "analyze revenue" in q:

        return [
            "Monthly revenue",
            "Revenue by state",
            "Top customers by revenue"
        ]


    # ---------------------------------------------------
    # Default behavior
    # ---------------------------------------------------

    # If no special case is detected,
    # simply return the original question.

    return [question]