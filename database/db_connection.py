"""
db_connection.py

Manages PostgreSQL database connections using SQLAlchemy.
"""

import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from config.settings import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

logger = logging.getLogger(__name__)

# Module-level engine (reused across calls)
_engine = None


def get_engine():
    """
    Create or return the SQLAlchemy engine.

    Uses a module-level singleton to avoid creating
    a new connection pool on every call.

    Returns
    -------
    sqlalchemy.Engine

    Raises
    ------
    ConnectionError
        If the database is unreachable.
    """
    global _engine

    if _engine is not None:
        return _engine

    connection_string = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    try:
        _engine = create_engine(
            connection_string,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
        )
        # Test the connection
        with _engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        logger.info("Database connection established successfully.")
        return _engine

    except OperationalError as e:
        logger.error("Failed to connect to database: %s", e)
        raise ConnectionError(
            f"Cannot connect to PostgreSQL at {DB_HOST}:{DB_PORT}/{DB_NAME}. "
            "Please check that the database is running and credentials are correct."
        ) from e
