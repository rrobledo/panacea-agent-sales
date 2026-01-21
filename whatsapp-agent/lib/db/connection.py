import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from lib.config import POSTGRES_URL


@contextmanager
def get_connection():
    """Get database connection with automatic cleanup"""
    conn = psycopg2.connect(POSTGRES_URL, cursor_factory=RealDictCursor)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def execute_query(query: str, params: tuple = None, fetch_one: bool = False):
    """Execute a query and return results"""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            if fetch_one:
                return cur.fetchone()
            return cur.fetchall()


def execute_write(query: str, params: tuple = None):
    """Execute a write query (INSERT, UPDATE, DELETE)"""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            if cur.description:
                return cur.fetchone()
            return None
