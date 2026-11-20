"""SQLite storage for price alerts."""

import sqlite3
from contextlib import closing

DB_PATH = "alerts.db"


def connect() -> sqlite3.Connection:
    """Open a connection whose rows can be read by column name, e.g. row["coin"]."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create the alerts table if it does not exist yet."""
    with closing(connect()) as conn, conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id      INTEGER NOT NULL,
                coin         TEXT    NOT NULL,
                direction    TEXT    NOT NULL CHECK (direction IN ('above', 'below')),
                target_price REAL    NOT NULL,
                created_at   TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)


def add_alert(chat_id: int, coin: str, direction: str, target_price: float) -> int:
    """Save a new alert and return its id."""
    with closing(connect()) as conn, conn:
        cursor = conn.execute(
            "INSERT INTO alerts (chat_id, coin, direction, target_price) VALUES (?, ?, ?, ?)",
            (chat_id, coin, direction, target_price),
        )
        return cursor.lastrowid


def get_alerts(chat_id: int) -> list[sqlite3.Row]:
    """Return all alerts of one chat, oldest first."""
    with closing(connect()) as conn:
        return conn.execute(
            "SELECT * FROM alerts WHERE chat_id = ? ORDER BY id", (chat_id,)
        ).fetchall()


def get_all_alerts() -> list[sqlite3.Row]:
    """Return the alerts of all chats, for the background price check."""
    with closing(connect()) as conn:
        return conn.execute("SELECT * FROM alerts ORDER BY id").fetchall()


def delete_alert(chat_id: int, alert_id: int) -> bool:
    """Delete an alert if it belongs to this chat. Return True if one was deleted."""
    with closing(connect()) as conn, conn:
        cursor = conn.execute(
            "DELETE FROM alerts WHERE id = ? AND chat_id = ?", (alert_id, chat_id)
        )
        return cursor.rowcount > 0
