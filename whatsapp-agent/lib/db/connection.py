import json
import asyncpg
from lib.config import POSTGRES_URL

_pool: asyncpg.Pool | None = None


async def _init_connection(conn: asyncpg.Connection):
    """Register JSON/JSONB codecs so columns auto-decode to Python dicts/lists."""
    await conn.set_type_codec(
        "jsonb",
        encoder=json.dumps,
        decoder=json.loads,
        schema="pg_catalog",
    )
    await conn.set_type_codec(
        "json",
        encoder=json.dumps,
        decoder=json.loads,
        schema="pg_catalog",
    )


async def get_pool() -> asyncpg.Pool:
    """Return a lazily-created connection pool (singleton)."""
    global _pool
    if _pool is None:
        dsn = POSTGRES_URL
        # Vercel provides postgres://, asyncpg requires postgresql://
        if dsn.startswith("postgres://"):
            dsn = dsn.replace("postgres://", "postgresql://", 1)
        _pool = await asyncpg.create_pool(dsn=dsn, min_size=1, max_size=5, init=_init_connection)
    return _pool


async def close_pool():
    """Close the connection pool."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


async def execute_query(query: str, params: tuple = None, fetch_one: bool = False):
    """Execute a query and return results as list[dict] or dict."""
    pool = await get_pool()
    args = params or ()
    async with pool.acquire() as conn:
        if fetch_one:
            row = await conn.fetchrow(query, *args)
            return dict(row) if row else None
        rows = await conn.fetch(query, *args)
        return [dict(r) for r in rows]


async def execute_write(query: str, params: tuple = None):
    """Execute a write query (INSERT, UPDATE, DELETE) and return the row if RETURNING is used."""
    pool = await get_pool()
    args = params or ()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, *args)
        return dict(row) if row else None
