from __future__ import annotations
import json
import time
import base64
from typing import Any
import httpx
from app.adapters.base import BaseChatAdapter
from app.schemas.chat import ChatRequest, ChatResponse
from app.config import (
    CODEX_RESPONSES_URL, TOKEN_URL, OPENAI_OAUTH_CLIENT_ID,
    DEFAULT_CODEX_INSTRUCTIONS, DEFAULT_CODEX_REASONING,
)


def _decode_jwt_payload(token: str) -> dict | None:
    parts = token.split(".")
    if len(parts) < 2:
        return None
    try:
        pad = len(parts[1]) % 4
        padded = parts[1] + "=" * (4 - pad) if pad else parts[1]
        return json.loads(base64.b64decode(padded.replace("-", "+").replace("_", "/")))
    except Exception:
        return None


def _extract_account_id(token: str) -> str | None:
    payload = _decode_jwt_payload(token)
    if not payload:
        return None
    auth = payload.get("https://api.openai.com/auth", {})
    return auth.get("chatgpt_account_id")


def _normalize_auth(raw: Any) -> dict:
    if isinstance(raw, str):
        raw = raw.strip()
        raw = json.loads(raw) if raw.startswith("{") else {"access": raw}
    if not isinstance(raw, dict):
        raise ValueError("auth inválido")
    access = raw.get("access") or raw.get("access_token")
    if not access:
        raise ValueError("auth: access_token ausente")
    refresh = raw.get("refresh") or raw.get("refresh_token")
    expires = raw.get("expires") or raw.get("expires_at")
    if expires:
        expires = int(str(expires))
        if expires < 1_000_000_000_000:
            expires *= 1000
    return {
        "access": access, "refresh": refresh, "expires": expires,
        "accountId": raw.get("accountId") or _extract_account_id(access),
    }


async def _maybe_refresh(auth: dict) -> dict:
    if not auth.get("refresh"):
        return auth
    expires = auth.get("expires")
    if expires and expires > int(time.time() * 1000) + 300_000:
        return auth
    async with httpx.AsyncClient() as client:
        resp = await client.post(TOKEN_URL, data={
            "grant_type": "refresh_token",
            "refresh_token": auth["refresh"],
            "client_id": OPENAI_OAUTH_CLIENT_ID,
        })
        resp.raise_for_status()
        data = resp.json()
    return {
        "access": data["access_token"],
        "refresh": data.get("refresh_token", auth["refresh"]),
        "expires": int(time.time() * 1000) + int(data.get("expires_in", 0)) * 1000,
        "accountId": auth.get("accountId") or _extract_account_id(data["access_token"]),
    }


def _parse_sse(raw: str) -> dict:
    delta_parts: list[str] = []
    final_text: list[str] = []
    tool_calls: list[dict] = []
    usage = None
    response_id = None

    for line in raw.splitlines():
        if not line.startswith("data:"):
            continue
        chunk = line[5:].strip()
        if not chunk or chunk == "[DONE]":
            continue
        try:
            event = json.loads(chunk)
        except Exception:
            continue
        if not response_id:
            response_id = event.get("response_id") or event.get("id")
        if event.get("type") == "response.completed":
            resp = event.get("response", {})
            usage = resp.get("usage")
            for item in resp.get("output", []):
                for part in item.get("content", []):
                    if isinstance(part.get("text"), str):
                        final_text.append(part["text"])
                if item.get("type") == "function_call":
                    call_id = item.get("call_id", "")
                    raw_args = item.get("arguments", "{}")
                    try:
                        parsed = json.loads(raw_args)
                    except Exception:
                        parsed = {}
                    tool_calls.append({
                        "id": item.get("id", call_id), "call_id": call_id,
                        "name": item.get("name", ""), "arguments": parsed, "arguments_raw": raw_args,
                    })
        delta = event.get("delta")
        if isinstance(delta, str):
            delta_parts.append(delta)

    text = "".join(delta_parts) or "".join(final_text)
    return {"id": response_id, "output_text": text.strip(), "tool_calls": tool_calls, "usage": usage}


def _build_context(messages: list[dict], limit: int) -> list[dict]:
    limit = max(2, min(200, int(limit or 40)))
    source = messages[-limit:] if len(messages) > limit else messages
    out = []
    for msg in source:
        role = "assistant" if msg.get("role") == "model" else msg.get("role")
        if role not in ("user", "assistant"):
            continue
        text = str(msg.get("text") or "").strip()
        if not text:
            continue
        content_type = "output_text" if role == "assistant" else "input_text"
        out.append({"role": role, "content": [{"type": content_type, "text": text}]})
    return out


class CodexAdapter(BaseChatAdapter):
    async def chat(self, request: ChatRequest) -> ChatResponse:
        auth = _normalize_auth(request.auth)
        auth = await _maybe_refresh(auth)

        messages = request.input or _build_context(request.messages, request.history_limit)
        headers = {
            "Authorization": f"Bearer {auth['access']}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        }
        if auth.get("accountId"):
            headers["chatgpt-account-id"] = auth["accountId"]

        body: dict = {
            "model": request.model,
            "input": messages,
            "store": False,
            "stream": True,
            "reasoning": {"effort": request.reasoning or DEFAULT_CODEX_REASONING},
            "instructions": request.instructions or DEFAULT_CODEX_INSTRUCTIONS,
        }
        if request.tools:
            body["tools"] = [t for t in request.tools if t.get("type") == "function"]

        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(CODEX_RESPONSES_URL, headers=headers, json=body)
            raw = resp.text
            resp.raise_for_status()

        parsed = _parse_sse(raw)
        return ChatResponse(
            provider="codex", model=request.model,
            message=parsed["output_text"],
            tool_calls=parsed["tool_calls"],
            usage=parsed["usage"],
            auth=auth,
            payload=parsed,
        )
