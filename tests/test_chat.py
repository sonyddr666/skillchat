from unittest.mock import AsyncMock, patch
from app.schemas.chat import ChatResponse

CODEX_PAYLOAD = {
    "provider": "codex",
    "model": "gpt-5.4-mini",
    "auth": {"access": "fake-token"},
    "messages": [{"role": "user", "text": "Ol\u00e1"}],
}

GEMINI_PAYLOAD = {
    "provider": "gemini",
    # gemini-2.5-flash: substituto oficial do gemini-2.0-flash (depreciado jun/2026)
    "model": "gemini-2.5-flash",
    "auth": {"api_key": "fake-key"},
    "messages": [{"role": "user", "text": "Ol\u00e1"}],
}

MOCK_RESPONSE = ChatResponse(
    provider="codex", model="gpt-5.4-mini",
    message="Ol\u00e1! Como posso ajudar?",
    tool_calls=[], usage=None,
    auth={"access": "fake-token"},
    payload={"output_text": "Ol\u00e1! Como posso ajudar?"},
)


def test_chat_codex_mocked(auth_client):
    with patch("app.routers.chat._adapters") as mock_adapters:
        adapter = AsyncMock()
        adapter.chat = AsyncMock(return_value=MOCK_RESPONSE)
        mock_adapters.get.return_value = adapter
        r = auth_client.post("/api/chat", json=CODEX_PAYLOAD)
    assert r.status_code == 200
    assert r.json()["message"] == "Ol\u00e1! Como posso ajudar?"


def test_chat_gemini_mocked(auth_client):
    gemini_resp = MOCK_RESPONSE.model_copy(update={"provider": "gemini", "model": "gemini-2.5-flash"})
    with patch("app.routers.chat._adapters") as mock_adapters:
        adapter = AsyncMock()
        adapter.chat = AsyncMock(return_value=gemini_resp)
        mock_adapters.get.return_value = adapter
        r = auth_client.post("/api/chat", json=GEMINI_PAYLOAD)
    assert r.status_code == 200
    assert r.json()["provider"] == "gemini"


def test_chat_unsupported_provider(auth_client):
    r = auth_client.post("/api/chat", json={**CODEX_PAYLOAD, "provider": "unknown"})
    assert r.status_code == 400


def test_chat_missing_auth(auth_client):
    r = auth_client.post("/api/chat", json={**CODEX_PAYLOAD, "auth": None})
    assert r.status_code in (400, 422)
