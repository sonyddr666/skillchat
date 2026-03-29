from pydantic import BaseModel, field_validator


class SkillPayload(BaseModel):
    id: str = ""
    name: str
    description: str
    icon: str = "⚙"
    enabled: bool = True
    builtin: bool = False
    parameters: dict = {}
    action: dict | None = None
    code: str | None = None

    @field_validator("builtin")
    @classmethod
    def no_builtin(cls, v: bool) -> bool:
        if v:
            raise ValueError("Builtin skills cannot be persisted")
        return v


class SkillOut(BaseModel):
    id: str
    name: str
    description: str
    icon: str
    enabled: bool
    builtin: bool
    parameters: dict
    action: dict | None = None
    code: str | None = None
