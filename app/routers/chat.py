from fastapi import APIRouter, HTTPException
from app.dependencies import CurrentUser
from app.schemas.chat import ChatRequest, ChatResponse
from app.adapters.codex import CodexAdapter
from app.adapters.gemini import GeminiAdapter

router = APIRouter(prefix="/api")
_adapters = {"codex": CodexAdapter(), "gemini": GeminiAdapter()}


@router.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest, user: CurrentUser):
    provider = body.provider.strip().lower()
    adapter = _adapters.get(provider)
    if not adapter:
        raise HTTPException(status_code=400, detail=f"Provider '{provider}' não suportado")
    if not body.auth:
        raise HTTPException(status_code=400, detail="auth ausente")
    if not body.model:
        raise HTTPException(status_code=400, detail="model ausente")
    if not body.messages and not body.input:
        raise HTTPException(status_code=400, detail="messages/input ausente")
    try:
        return await adapter.chat(body)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc))
