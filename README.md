# SkillChat

Rewrite do **SkillFlow Chat** em Python — `FastAPI + Pydantic v2 + SQLite`.

## Instalação

```bash
pip install -r requirements.txt
```

## Executar

```bash
uvicorn app.main:app --host 0.0.0.0 --port 9321 --reload
```

## Testes

```bash
pip install -r requirements-dev.txt
pytest
```

## Estrutura

```
app/
  main.py          — FastAPI app + startup
  config.py        — env vars e constantes
  database.py      — SQLite + DDL
  dependencies.py  — CurrentUser, DBDep
  routers/         — health, auth, state, skills, filesystem, chat
  schemas/         — Pydantic v2 models
  services/        — auth, state, skills, fs
  adapters/        — codex, gemini
data/              — runtime (db + workspaces + skills + attachments)
docs/              — functional-spec.md
tests/             — suite completa pytest
```

## APIs MVP

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/health` | Health check |
| POST | `/auth/register` | Criar conta |
| POST | `/auth/login` | Login |
| POST | `/auth/logout` | Logout |
| GET | `/auth/me` | Usuário atual |
| GET/POST | `/api/state` | Estado do usuário |
| GET/POST/DELETE | `/api/skills` | Skills customizadas |
| GET | `/api/fs/list` | Listar arquivos |
| GET | `/api/fs/read` | Ler arquivo |
| GET | `/api/fs/download` | Download de arquivo |
| POST | `/api/fs/write` | Escrever arquivo |
| POST | `/api/fs/mkdir` | Criar diretório |
| POST | `/api/fs/rename` | Renomear |
| DELETE | `/api/fs/delete` | Deletar |
| POST | `/api/chat` | Chat (Codex / Gemini) |

Veja [docs/functional-spec.md](docs/functional-spec.md) para especificação completa.
