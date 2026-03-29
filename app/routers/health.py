from fastapi import APIRouter
from app.config import PORT

router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "ok", "service": "skillchat", "version": "0.1.0", "port": PORT}
