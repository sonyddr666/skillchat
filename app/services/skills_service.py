from __future__ import annotations
import json
import re
from pathlib import Path
from app.config import SKILLS_DIR


def _sanitize_id(value: str) -> str:
    v = re.sub(r"[^a-z0-9_-]+", "_", value.strip().lower())
    return v.strip("_")[:80]


def _skill_path(user_id: str, skill_id: str) -> Path:
    return SKILLS_DIR / user_id / f"{skill_id}.json"


def _normalize(raw: dict) -> dict:
    sid = _sanitize_id(raw.get("id") or raw.get("name") or "")
    name = str(raw.get("name") or "").strip()
    desc = str(raw.get("description") or "").strip()
    if not sid:
        raise ValueError("Skill id/name is required")
    if not name:
        raise ValueError("Skill name is required")
    if not desc:
        raise ValueError("Skill description is required")
    if raw.get("builtin"):
        raise ValueError("Builtin skills cannot be persisted")
    skill: dict = {
        "id": sid,
        "builtin": False,
        "enabled": raw.get("enabled", True) is not False,
        "icon": str(raw.get("icon") or "⚙").strip() or "⚙",
        "name": name,
        "description": desc,
        "parameters": raw.get("parameters") or {"type": "OBJECT", "properties": {}},
    }
    if isinstance(raw.get("action"), dict):
        skill["action"] = raw["action"]
    elif isinstance(raw.get("code"), str):
        skill["code"] = raw["code"]
    else:
        raise ValueError("Skill needs action or code")
    return skill


def list_skills(user_id: str) -> list[dict]:
    base = SKILLS_DIR / user_id
    base.mkdir(parents=True, exist_ok=True)
    skills = []
    for fp in sorted(base.glob("*.json")):
        try:
            skills.append(_normalize(json.loads(fp.read_text("utf-8"))))
        except Exception:
            pass
    return sorted(skills, key=lambda s: s["name"])


def upsert_skill(user_id: str, payload: dict) -> dict:
    skill = _normalize(payload)
    base = SKILLS_DIR / user_id
    base.mkdir(parents=True, exist_ok=True)
    _skill_path(user_id, skill["id"]).write_text(
        json.dumps(skill, indent=2, ensure_ascii=False) + "\n", "utf-8"
    )
    return skill


def delete_skill(user_id: str, skill_id: str) -> bool:
    fp = _skill_path(user_id, _sanitize_id(skill_id))
    if not fp.exists():
        return False
    fp.unlink()
    return True
