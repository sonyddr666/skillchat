from __future__ import annotations
from typing import Any
from pydantic import BaseModel


class ChatRequest(BaseModel):
    provider: str
    model: str
    auth: Any
    messages: list[dict] = []
    input: list[dict] | None = None
    tools: list[dict] = []
    attachments: list[dict] = []
    reasoning: str = "medium"
    history_limit: int = 40
    instructions: str = ""
    session_id: str = ""


class ChatResponse(BaseModel):
    ok: bool = True
    provider: str
    model: str
    message: str
    tool_calls: list[dict] = []
    usage: dict | None = None
    auth: Any
    payload: dict
