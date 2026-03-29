from __future__ import annotations
from abc import ABC, abstractmethod
from app.schemas.chat import ChatRequest, ChatResponse


class BaseChatAdapter(ABC):
    @abstractmethod
    async def chat(self, request: ChatRequest) -> ChatResponse:
        ...
