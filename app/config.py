import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

DB_PATH = DATA_DIR / "skillflow.db"
WORKSPACES_DIR = DATA_DIR / "workspaces"
SKILLS_DIR = DATA_DIR / "skills"
ATTACHMENTS_DIR = DATA_DIR / "attachments"

SESSION_TTL_SECONDS = 60 * 60 * 24 * 30  # 30 dias
SESSION_COOKIE_NAME = "sf_session"

PORT = int(os.getenv("PORT", "9321"))
HOST = os.getenv("HOST", "0.0.0.0")

DEFAULT_CODEX_MODEL = os.getenv("DEFAULT_CODEX_MODEL", "gpt-5.4-mini")
DEFAULT_CODEX_REASONING = "medium"
DEFAULT_CODEX_HISTORY_LIMIT = 40
DEFAULT_CODEX_INSTRUCTIONS = os.getenv(
    "SKILLFLOW_CODEX_DEFAULT_INSTRUCTIONS",
    "Responda em portugu\u00eas do Brasil e mantenha continuidade com base na conversa.",
)
CODEX_RESPONSES_URL = "https://chatgpt.com/backend-api/codex/responses"
OPENAI_OAUTH_CLIENT_ID = os.getenv("OPENAI_OAUTH_CLIENT_ID", "app_EMoamEEZ73f0CkXaXp7hrann")
TOKEN_URL = "https://auth.openai.com/oauth/token"

# gemini-2.0-flash depreciado em fev/2026, shutdown jun/2026
# substituto oficial: gemini-2.5-flash
# ref: https://ai.google.dev/gemini-api/docs/deprecations
DEFAULT_GEMINI_MODEL = os.getenv("DEFAULT_GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

STATE_KEYS = [
    "gc_cfg", "gc_theme", "gc_plugins", "gc_convs", "gc_user_memory",
    "gc_pending_approvals", "gc_skill_packs", "gc_tts_voice",
    "gc_tts_autoplay", "gc_sb_collapsed",
]
