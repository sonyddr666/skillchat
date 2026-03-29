from pydantic import BaseModel, field_validator


class RegisterRequest(BaseModel):
    login: str
    password: str

    @field_validator("login")
    @classmethod
    def login_min(cls, v: str) -> str:
        if len(v.strip()) < 3:
            raise ValueError("Login precisa ter pelo menos 3 caracteres")
        return v.strip().lower()

    @field_validator("password")
    @classmethod
    def password_min(cls, v: str) -> str:
        if len(v) < 4:
            raise ValueError("Senha precisa ter pelo menos 4 caracteres")
        return v


class LoginRequest(BaseModel):
    login: str
    password: str


class UserOut(BaseModel):
    id: str
    login: str
