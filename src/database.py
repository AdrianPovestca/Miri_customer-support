"""
database.py
-----------
Phase 5: Advanced Features — persistent conversation history.

Stores conversation messages in a SQLite database (a single file, no
separate server needed), so history survives API restarts — unlike the
in-memory session storage used in earlier phases.
"""

import sqlite3
import logging
from pathlib import Path
from typing import Dict, List

from config import BASE_DIR

logger = logging.getLogger(__name__)

DB_PATH = BASE_DIR / "conversations.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create the messages table if it doesn't exist yet. Safe to call every startup."""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_session_id ON messages (session_id)")
    conn.commit()
    conn.close()
    logger.info(f"Database ready at {DB_PATH}")


def save_message(session_id: str, role: str, content: str) -> None:
    conn = get_connection()
    conn.execute(
        "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
        (session_id, role, content),
    )
    conn.commit()
    conn.close()


def get_history(session_id: str) -> List[Dict]:
    """Returns messages in {"role": ..., "content": ...} form, oldest first."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT role, content FROM messages WHERE session_id = ? ORDER BY id ASC",
        (session_id,),
    ).fetchall()
    conn.close()
    return [{"role": row["role"], "content": row["content"]} for row in rows]


def clear_session(session_id: str) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()


def list_sessions() -> List[Dict]:
    """Used by the admin interface — one row per session, most recently active first."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT
            session_id,
            COUNT(*) as message_count,
            MIN(created_at) as started_at,
            MAX(created_at) as last_active
        FROM messages
        GROUP BY session_id
        ORDER BY last_active DESC
    """).fetchall()
    conn.close()
    return [dict(row) for row in rows]