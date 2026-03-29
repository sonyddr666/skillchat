from fastapi import APIRouter, HTTPException
from app.dependencies import CurrentUser
from app.schemas.skills import SkillPayload
from app.services import skills_service

router = APIRouter(prefix="/api")


@router.get("/skills")
async def list_skills(user: CurrentUser):
    return {"skills": skills_service.list_skills(user["id"])}


@router.post("/skills")
async def upsert_skill(body: SkillPayload, user: CurrentUser):
    try:
        skill = skills_service.upsert_skill(user["id"], body.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"ok": True, "skill": skill}


@router.delete("/skills/{skill_id}")
async def delete_skill(skill_id: str, user: CurrentUser):
    deleted = skills_service.delete_skill(user["id"], skill_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Skill not found")
    return {"ok": True, "id": skill_id}
