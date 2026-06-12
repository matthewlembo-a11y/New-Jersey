"""
Shared SQLite helpers for the Bergen County Fourth Round site inventory.

All state lives in db/bergen.db so every run is resumable. Nothing is ever
held only in conversation memory: research progress, sources, and extracted
sites are committed to the database (and exported to reports/) as we go.
"""
import os
import sqlite3
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT, "db", "bergen.db")


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def log(conn, municipality, action, detail=""):
    conn.execute(
        "INSERT INTO research_log(ts, municipality, action, detail) VALUES (?,?,?,?)",
        (now(), municipality, action, detail),
    )
    conn.commit()


def get_meta(conn, key, default=None):
    row = conn.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
    return row["value"] if row else default


def set_meta(conn, key, value):
    conn.execute(
        "INSERT INTO meta(key, value) VALUES (?,?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, str(value)),
    )
    conn.commit()
