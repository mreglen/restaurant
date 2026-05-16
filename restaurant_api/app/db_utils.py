"""Утилиты для работы с PostgreSQL (основная и тестовая БД)."""
from __future__ import annotations

from urllib.parse import urlsplit, urlunsplit


def resolve_test_database_url(database_url: str, test_database_url: str | None = None) -> str:
    if test_database_url:
        return test_database_url
    parts = urlsplit(database_url)
    db_name = parts.path.lstrip('/') or 'restaurant'
    return urlunsplit(
        (parts.scheme, parts.netloc, f'/{db_name}_test', parts.query, parts.fragment)
    )


def ensure_postgres_database(database_url: str) -> None:
    """Создаёт базу PostgreSQL, если её ещё нет."""
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

    parts = urlsplit(database_url)
    db_name = parts.path.lstrip('/')
    if not db_name or not parts.scheme.startswith('postgres'):
        return

    conn = psycopg2.connect(
        dbname='postgres',
        user=parts.username or 'postgres',
        password=parts.password or '',
        host=parts.hostname or 'localhost',
        port=parts.port or 5432,
    )
    try:
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cur:
            cur.execute('SELECT 1 FROM pg_database WHERE datname = %s', (db_name,))
            if cur.fetchone() is None:
                cur.execute(f'CREATE DATABASE "{db_name}"')
    finally:
        conn.close()
