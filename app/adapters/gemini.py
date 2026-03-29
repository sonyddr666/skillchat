from __future__ import annotations
from typing import Any
import httpx
from app.adapters.base import BaseChatAdapter
from app.schemas.chat import ChatRequest, ChatResponse
from app.config import GEMINI_BASE_URL, DEFAULT_GEMINI_MODEL


def _normalize_auth(raw: Any) -> str:
    if isinstance(raw, str):
        return raw.strip()
    if isinstance(raw, dict):
        return str(raw.get("api_key") or raw.get("key") or raw.get("access") or "").strip()
    raise ValueError("Gemini auth: api_key ausente")


def _build_contents(messages: list[dict]) -> list[dict]:
    out = []
    for msg in messages:
        role = "model" if msg.get("role") in ("model", "assistant") else "user"
        text = str(msg.get("text") or "").strip()
        if not text:
            continue
        out.append({"role": role, "parts": [{"text": text}]})
    return out


class GeminiAdapter(BaseChatAdapter):
    async def chat(self, request: ChatRequest) -> ChatResponse:
        api_key = _normalize_auth(request.auth)
        if not api_key:
            raise ValueError("Gemini auth: api_key ausente")

        model = request.model or DEFAULT_GEMINI_MODEL
        url = f"{GEMINI_BASE_URL}/{model}:generateContent?key={api_key}"
        contents = _build_contents(request.messages)
        if not contents:
            raise ValueError("Nenhuma mensagem válida para Gemini")

        body: dict = {"contents": contents}
        if request.instructions:
            body["systemInstruction"] = {"parts": [{"text": request.instructions}]}

        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(url, json=body)
            resp.raise_for_status()
            data = resp.json()

        candidates = data.get("candidates", [])
        text = ""
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            text = "".join(p.get("text", "") for p in parts).strip()

        usage = data.get("usageMetadata")
        return ChatResponse(
            provider="gemini", model=model,
            message=text, tool_calls=[], usage=usage,
            auth={"api_key": api_key},
            payload=data,
        )
