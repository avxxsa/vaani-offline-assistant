import sqlite3
from pathlib import Path
from datetime import datetime


# Database location
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "vaani.db"


# Internal helper
def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = _connect()
    cur = conn.cursor()

    # Chat messages
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        role TEXT,
        text TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )

    """)

    # Journal entries
    cur.execute("""
        CREATE TABLE IF NOT EXISTS journal_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # To-do list
    cur.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            completed INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Reminders
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT,
            remind_at DATETIME,
            triggered INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


# Chat helpers
def add_chat_message(session_id: str, role: str, text: str):
    conn = _connect()
    conn.execute(
        "INSERT INTO chat_messages (session_id, role, text) VALUES (?, ?, ?)",
        (session_id, role, text)
    )
    conn.commit()
    conn.close()


def get_chat_history(session_id: str, limit: int = 50):
    conn = _connect()
    rows = conn.execute(
        """
        SELECT role, text, created_at
        FROM chat_messages
        WHERE session_id = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (session_id, limit)
    ).fetchall()
    conn.close()
    return [dict(r) for r in reversed(rows)]


def clear_chat_session(session_id: str):
    conn = _connect()
    conn.execute("DELETE FROM chat_messages WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()


# Journal helpers
def add_journal_entry(content: str):
    conn = _connect()
    conn.execute(
        "INSERT INTO journal_entries (content) VALUES (?)",
        (content,)
    )
    conn.commit()
    conn.close()


def get_journal_entries(limit: int = 50):
    conn = _connect()
    rows = conn.execute(
        """
        SELECT id, content, created_at
        FROM journal_entries
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_journal_entry(entry_id: int):
    conn = _connect()
    conn.execute("DELETE FROM journal_entries WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()


# To-do helpers
def add_todo(title: str):
    conn = _connect()
    conn.execute(
        "INSERT INTO todos (title) VALUES (?)",
        (title,)
    )
    conn.commit()
    conn.close()


def get_todos():
    conn = _connect()
    rows = conn.execute(
        """
        SELECT id, title, completed, created_at
        FROM todos
        ORDER BY id DESC
        """
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def set_todo_completed(todo_id: int, completed: bool):
    conn = _connect()
    conn.execute(
        "UPDATE todos SET completed = ? WHERE id = ?",
        (1 if completed else 0, todo_id)
    )
    conn.commit()
    conn.close()


def delete_todo(todo_id: int):
    conn = _connect()
    conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    conn.commit()
    conn.close()


# Reminder helpers
def add_reminder(text: str, remind_at: datetime):
    conn = _connect()
    conn.execute(
        "INSERT INTO reminders (text, remind_at) VALUES (?, ?)",
        (text, remind_at.isoformat())
    )
    conn.commit()
    conn.close()


def get_pending_reminders(now: datetime | None = None):
    if now is None:
        now = datetime.now()

    conn = _connect()
    rows = conn.execute(
        """
        SELECT id, text, remind_at
        FROM reminders
        WHERE triggered = 0 AND remind_at <= ?
        """,
        (now.isoformat(),)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def mark_reminder_triggered(reminder_id: int):
    conn = _connect()
    conn.execute(
        "UPDATE reminders SET triggered = 1 WHERE id = ?",
        (reminder_id,)
    )
    conn.commit()
    conn.close()
