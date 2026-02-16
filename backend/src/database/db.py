"""SQLite connection manager for tax calculation persistence."""

import sqlite3
from pathlib import Path

# Database file lives at backend/tax_data.db
DB_PATH: Path = Path(__file__).resolve().parent.parent.parent / "tax_data.db"
_SCHEMA_PATH: Path = Path(__file__).resolve().parent / "schema.sql"

_connection: sqlite3.Connection | None = None


def init_db() -> sqlite3.Connection:
    """Create (or open) the database and apply the schema. Returns the connection."""
    global _connection
    _connection = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    _connection.row_factory = sqlite3.Row
    schema = _SCHEMA_PATH.read_text()
    _connection.executescript(schema)
    return _connection


def get_db() -> sqlite3.Connection:
    """Return the module-level connection, creating it if necessary."""
    global _connection
    if _connection is None:
        return init_db()
    return _connection


def close_db() -> None:
    """Close the connection if open."""
    global _connection
    if _connection is not None:
        _connection.close()
        _connection = None
