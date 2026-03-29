from __future__ import annotations
import re
import sqlite3
import time
from secrets import token_hex
from datetime import datetime, timezone

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.config import SESSION_TTL_SECONDS, WORKSPACES_DIR, SKILLS_DIR, ATTACHMENTS_DIR

_ph = PasswordHasher()


def sanitize_id(value: str) -> str:
    v = re.sub(r"[^a-z0-9_-]+", "_", value.strip().lower())
    v = v.strip("_")[:80]
    return v


def hash_password(password: str) -> str:
    return _ph.hash(password)


def verify_password(password: str, stored: str) -> bool:
    try:
        return _ph.verify(stored, password)
    except VerifyMismatchError:
        return False
    except Exception:
        return False


def _ensure_user_dirs(user_id: str) -> None:
    for base in (WORKSPACES_DIR, SKILLS_DIR, ATTACHMENTS_DIR):
        (base / user_id).mkdir(parents=True, exist_ok=True)


def create_user(db: sqlite3.Connection, login: str, password: str) -> dict:
    login = login.strip().lower()
    if len(login) < 3:
        raise ValueError("Login precisa ter pelo menos 3 caracteres")
    if len(password) < 4:
        raise ValueError("Senha precisa ter pelo menos 4 caracteres")

    uid = sanitize_id(login)
    now = datetime.now(timezone.utc).isoformat()
    try:
        db.execute(
            "INSERT INTO users (id, login, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (uid, login, hash_password(password), now),
        )
        db.execute(
            "INSERT OR IGNORE INTO user_state (user_id, data) VALUES (?, '{}')",
            (uid,),
        )
        db.commit()
    except sqlite3.IntegrityError:
        raise ValueError("Login já existe")
    _ensure_user_dirs(uid)
    return {"id": uid, "login": login, "created_at": now}


def authenticate_user(db: sqlite3.Connection, login: str, password: str) -> dict | None:
    login = login.strip().lower()
    row = db.execute("SELECT * FROM users WHERE login = ?", (login,)).fetchone()
    if not row:
        return None
    if not verify_password(password, row["password_hash"]):
        return None
    _ensure_user_dirs(row["id"])
    return dict(row)


def create_session(db: sqlite3.Connection, user_id: str) -> str:
    token = token_hex(24)
    expires_at = int(time.time() * 1000) + SESSION_TTL_SECONDS * 1000
    db.execute(
        "INSERT INTO sessions (token, user_id, expires_at) VALUES (?, ?, ?)",
        (token, user_id, expires_at),
    )
    db.commit()
    return token


def destroy_session(db: sqlite3.Connection, token: str) -> None:
    db.execute("DELETE FROM sessions WHERE token = ?", (token,))
    db.commit()
