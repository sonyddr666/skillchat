from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routers import auth, chat, filesystem, health, skills, state

app = FastAPI(title="SkillChat", version="0.1.0", description="SkillFlow Chat — rewrite Python")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(state.router)
app.include_router(skills.router)
app.include_router(filesystem.router)
app.include_router(chat.router)


@app.on_event("startup")
def on_startup():
    init_db()
