from __future__ import annotations
import json
import sqlite3
from app.config import STATE_KEYS


def load_state(db: sqlite3.Connection, user_id: str) -> dict:
    row = db.execute("SELECT data FROM user_state WHERE user_id = ?", (user_id,)).fetchone()
    if not row:
        return {}
    try:
        return json.loads(row["data"])
    except Exception:
        return {}


def save_state(db: sqlite3.Connection, user_id: str, incoming: dict) -> None:
    current = load_state(db, user_id)
    for key in STATE_KEYS:
        if key in incoming:
            current[key] = incoming[key]
    db.execute(
        "INSERT INTO user_state (user_id, data) VALUES (?, ?) "
        "ON CONFLICT(user_id) DO UPDATE SET data = excluded.data",
        (user_id, json.dumps(current)),
    )
    db.commit()
