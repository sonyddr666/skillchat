from __future__ import annotations
import os
from pathlib import Path
from app.config import WORKSPACES_DIR


def _user_root(user_id: str) -> Path:
    root = WORKSPACES_DIR / user_id
    root.mkdir(parents=True, exist_ok=True)
    return root


def resolve_path(user_id: str, rel: str) -> Path:
    root = _user_root(user_id)
    rel_clean = rel.replace("\\", "/").lstrip("/").strip()
    candidate = (root / rel_clean).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        raise PermissionError("Path escapes user workspace root")
    return candidate


def _mtime(st: os.stat_result) -> str:
    from datetime import datetime, timezone
    return datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat()


def list_dir(user_id: str, rel: str) -> dict:
    path = resolve_path(user_id, rel)
    items = []
    for entry in sorted(path.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower())):
        st = entry.stat()
        items.append({
            "name": entry.name,
            "path": str(entry.relative_to(_user_root(user_id))),
            "type": "directory" if entry.is_dir() else "file",
            "size": st.st_size,
            "updated_at": _mtime(st),
        })
    return {"path": rel.strip("/"), "items": items}


def read_file(user_id: str, rel: str) -> dict:
    path = resolve_path(user_id, rel)
    if not path.is_file():
        raise IsADirectoryError("Path is not a file")
    st = path.stat()
    return {
        "path": rel.strip("/"),
        "type": "file",
        "size": st.st_size,
        "updated_at": _mtime(st),
        "content": path.read_text("utf-8", errors="replace"),
    }


def write_file(user_id: str, rel: str, content: str, encoding: str = "utf-8", create_dirs: bool = True) -> dict:
    path = resolve_path(user_id, rel)
    if create_dirs:
        path.parent.mkdir(parents=True, exist_ok=True)
    if encoding.lower() == "base64":
        import base64
        path.write_bytes(base64.b64decode(content))
    else:
        path.write_text(content, "utf-8")
    st = path.stat()
    return {"ok": True, "path": rel.strip("/"), "type": "file", "size": st.st_size, "updated_at": _mtime(st)}


def make_dir(user_id: str, rel: str) -> dict:
    path = resolve_path(user_id, rel)
    path.mkdir(parents=True, exist_ok=True)
    return {"ok": True, "path": rel.strip("/"), "type": "directory"}


def rename_entry(user_id: str, rel_from: str, rel_to: str) -> dict:
    src = resolve_path(user_id, rel_from)
    dst = resolve_path(user_id, rel_to)
    dst.parent.mkdir(parents=True, exist_ok=True)
    src.rename(dst)
    st = dst.stat()
    return {
        "ok": True,
        "from": rel_from.strip("/"),
        "to": rel_to.strip("/"),
        "type": "directory" if dst.is_dir() else "file",
        "size": st.st_size,
        "updated_at": _mtime(st),
    }


def delete_entry(user_id: str, rel: str) -> dict:
    import shutil
    path = resolve_path(user_id, rel)
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()
    return {"ok": True, "path": rel.strip("/")}
