from __future__ import annotations
import time
import sqlite3
from typing import Annotated
from fastapi import Cookie, Depends, HTTPException, status
from app.database import get_db
from app.config import SESSION_COOKIE_NAME


def db_dep() -> sqlite3.Connection:
    return get_db()


DBDep = Annotated[sqlite3.Connection, Depends(db_dep)]


def get_current_user(
    db: DBDep,
    sf_session: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
) -> dict:
    if not sf_session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    now_ms = int(time.time() * 1000)
    row = db.execute(
        """
        SELECT u.id, u.login, u.created_at
        FROM sessions s
        JOIN users u ON u.id = s.user_id
        WHERE s.token = ? AND s.expires_at > ?
        """,
        (sf_session, now_ms),
    ).fetchone()
    if not row:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return dict(row)


CurrentUser = Annotated[dict, Depends(get_current_user)]
