from fastapi import APIRouter
from app.dependencies import DBDep, CurrentUser
from app.schemas.state import StateSaveRequest
from app.services import state_service

router = APIRouter(prefix="/api")


@router.get("/state")
async def get_state(user: CurrentUser, db: DBDep):
    return {"state": state_service.load_state(db, user["id"])}


@router.post("/state")
async def post_state(body: StateSaveRequest, user: CurrentUser, db: DBDep):
    state_service.save_state(db, user["id"], body.state)
    return {"ok": True}
