from pydantic import BaseModel


class StateSaveRequest(BaseModel):
    state: dict = {}
