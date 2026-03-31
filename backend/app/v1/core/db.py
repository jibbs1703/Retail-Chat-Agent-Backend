"""Retail Chat Agent — PostgreSQL Database Utilities."""

import psycopg2
import psycopg2.extras

from .configuration import get_settings


def get_product_by_id(product_id: int) -> dict | None:
    """Fetch a product row from PostgreSQL by its primary key.

    Args:
        product_id: The product's integer primary key (matches ``product_id``
                    stored in the Qdrant payload).

    Returns:
        A dict of column-name → value for the matching row, or ``None`` if the
        product does not exist or the database is unreachable.
    """
    settings = get_settings()
    conn = None
    try:
        conn = psycopg2.connect(
            host=settings.postgres_host,
            port=settings.postgres_port,
            dbname=settings.postgres_database,
            user=settings.postgres_user,
            password=settings.postgres_password,
        )
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM products WHERE id = %s", (product_id,))
            row = cur.fetchone()
            return dict(row) if row else None
    except Exception:
        return None
    finally:
        if conn:
            conn.close()
