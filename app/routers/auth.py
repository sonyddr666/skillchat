from fastapi import APIRouter, HTTPException, Response
from app.dependencies import DBDep, CurrentUser
from app.schemas.auth import LoginRequest, RegisterRequest, UserOut
from app.services import auth_service
from app.config import SESSION_COOKIE_NAME, SESSION_TTL_SECONDS

router = APIRouter(prefix="/auth")


def _set_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        SESSION_COOKIE_NAME, token,
        max_age=SESSION_TTL_SECONDS, httponly=True,
        samesite="lax", path="/",
    )


@router.post("/register")
async def register(body: RegisterRequest, response: Response, db: DBDep):
    try:
        user = auth_service.create_user(db, body.login, body.password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    token = auth_service.create_session(db, user["id"])
    _set_cookie(response, token)
    return {"ok": True, "user": UserOut(id=user["id"], login=user["login"])}


@router.post("/login")
async def login(body: LoginRequest, response: Response, db: DBDep):
    user = auth_service.authenticate_user(db, body.login, body.password)
    if not user:
        raise HTTPException(status_code=401, detail="Login ou senha inválidos")
    token = auth_service.create_session(db, user["id"])
    _set_cookie(response, token)
    return {"ok": True, "user": UserOut(id=user["id"], login=user["login"])}


@router.post("/logout")
async def logout(response: Response, user: CurrentUser, db: DBDep):
    response.delete_cookie(SESSION_COOKIE_NAME, path="/")
    return {"ok": True}


@router.get("/me")
async def me(user: CurrentUser):
    return {"user": UserOut(id=user["id"], login=user["login"])}
