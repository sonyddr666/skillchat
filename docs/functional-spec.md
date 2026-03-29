# SkillFlow Chat — Especificação Funcional

> Idioma: pt-BR  
> Versão: 0.1.0-draft  
> Fonte de verdade: `server.js` (Node) + `public/index.html`  
> Status: MVP em definição

---

## 1. Visão Geral

O **SkillFlow Chat** é uma aplicação web de chat com IA que permite ao usuário
conversar com modelos de linguagem (Codex/OpenAI e Gemini), gerenciar skills
customizadas, persistir estado de conversa e operar um workspace de arquivos
isolado por conta de usuário.

Este documento especifica o rewrite do backend em **Python (FastAPI)**, mantendo
compatibilidade de contrato com o frontend existente.

---

## 2. Objetivos

- Reproduzir o núcleo operacional do produto atual (Node/server.js) em Python.
- Manter compatibilidade de API com o frontend `index.html` existente.
- Isolamento forte por usuário (dados, skills, workspace, sessão).
- Suporte a dois providers de LLM: família Codex/OpenAI e família Gemini.
- Arquitetura testável: adapters mockáveis, serviços independentes.

---

## 3. Módulos

| Módulo            | Responsabilidade                                      |
|-------------------|-------------------------------------------------------|
| `auth`            | Registro, login, logout, sessão opaca por cookie      |
| `chat`            | Dispatcher de providers, normalização de resposta     |
| `state`           | Leitura e merge seguro de estado do usuário           |
| `skills`          | CRUD de skills customizadas por usuário               |
| `filesystem`      | Operações de arquivo no workspace isolado do usuário  |
| `attachments`     | Persistência e referência de anexos do chat           |

---

## 4. Stack

```
FastAPI >= 0.111
Pydantic v2
SQLite (via aiosqlite ou sqlite3 síncrono em thread pool)
argon2-cffi (hash de senha Argon2id)
pytest + httpx (testes)
uvicorn (servidor ASGI)
```

---

## 5. Estrutura de Diretórios

```
skillchat/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── dependencies.py
│   ├── routers/
│   │   ├── auth.py
│   │   ├── chat.py
│   │   ├── state.py
│   │   ├── skills.py
│   │   ├── filesystem.py
│   │   └── health.py
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── chat.py
│   │   ├── state.py
│   │   ├── skills.py
│   │   └── filesystem.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── state_service.py
│   │   ├── skills_service.py
│   │   └── fs_service.py
│   └── adapters/
│       ├── base.py
│       ├── codex.py
│       └── gemini.py
├── data/
│   ├── workspaces/
│   ├── skills/
│   └── attachments/
├── docs/
│   └── functional-spec.md
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_state.py
│   ├── test_skills.py
│   ├── test_filesystem.py
│   └── test_chat.py
├── requirements.txt
├── requirements-dev.txt
└── pyproject.toml
```

---

## 6. Persistência

### 6.1 SQLite — tabelas

**`users`**
```sql
CREATE TABLE users (
    id          TEXT PRIMARY KEY,
    login       TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at  TEXT NOT NULL
);
```

**`sessions`**
```sql
CREATE TABLE sessions (
    token       TEXT PRIMARY KEY,
    user_id     TEXT NOT NULL REFERENCES users(id),
    expires_at  INTEGER NOT NULL
);
```

**`user_state`**
```sql
CREATE TABLE user_state (
    user_id     TEXT PRIMARY KEY REFERENCES users(id),
    data        TEXT NOT NULL DEFAULT '{}'
);
```

### 6.2 Filesystem

```
data/workspaces/<user-id>/
data/skills/<user-id>/
data/attachments/<user-id>/
```

Regra de isolamento: qualquer `path` resolvido fora da raiz do usuário retorna **400 Path escapes user root**.

---

## 7. Autenticação

| Rota              | Método | Auth obrigatória | Descrição               |
|-------------------|--------|------------------|-------------------------|
| `/auth/register`  | POST   | Não              | Cria conta              |
| `/auth/login`     | POST   | Não              | Inicia sessão           |
| `/auth/logout`    | POST   | Sim              | Encerra sessão          |
| `/auth/me`        | GET    | Sim              | Retorna usuário atual   |

- Senha: hash **Argon2id** via `argon2-cffi`.
- Cookie: `sf_session=<token opaco>; HttpOnly; SameSite=Lax; Path=/`.
- Sessão: persistida em `sessions` (SQLite), TTL 30 dias.
- Sessão sobrevive restart do servidor.

---

## 8. APIs do MVP

### 8.1 Health

```
GET /health
→ 200 { status, service, version, authenticated }
```

### 8.2 Estado do usuário

```
GET  /api/state         → 200 { state: {...} }
POST /api/state         body: { state: { gc_cfg?, gc_theme?, ... } }
                        → 200 { ok: true }
```

Chaves permitidas no merge:
`gc_cfg`, `gc_theme`, `gc_plugins`, `gc_convs`, `gc_user_memory`,
`gc_pending_approvals`, `gc_skill_packs`, `gc_tts_voice`,
`gc_tts_autoplay`, `gc_sb_collapsed`

### 8.3 Skills customizadas

```
GET    /api/skills          → 200 { skills: [...] }
POST   /api/skills          body: SkillPayload → 200 { ok, skill }
DELETE /api/skills/{id}     → 200 { ok, id }
```

### 8.4 Filesystem

```
GET    /api/fs/list?path=
GET    /api/fs/read?path=
GET    /api/fs/download?path=
POST   /api/fs/write
POST   /api/fs/mkdir
POST   /api/fs/rename
DELETE /api/fs/delete?path=
```

### 8.5 Chat

```
POST /api/chat
body: { provider, model, auth, messages, input, tools, attachments,
        reasoning, history_limit, instructions, session_id }
response: { ok, provider, model, message, tool_calls, usage, auth, payload }
```

---

## 9. Modelos Suportados (MVP)

### Família Codex / OpenAI
- Endpoint: `https://chatgpt.com/backend-api/codex/responses`
- Auth: access token + refresh token opcional (OAuth)
- Formato: SSE streaming, parseado internamente
- Default model: `gpt-5.4-mini`

### Família Gemini
- Endpoint: `https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent`
- Auth: API Key por request
- Formato: JSON síncrono
- Default model: `gemini-2.0-flash`

---

## 10. Contrato Interno do Chat

```python
class ChatRequest(BaseModel):
    provider: str
    model: str
    auth: dict | str
    messages: list[dict]
    input: list[dict] | None = None
    tools: list[dict] = []
    attachments: list[dict] = []
    reasoning: str = "medium"
    history_limit: int = 40
    instructions: str = ""
    session_id: str = ""

class ChatResponse(BaseModel):
    message: str
    tool_calls: list[dict] = []
    usage: dict | None = None
    auth: dict
    raw: dict
```

---

## 11. Limites e Fora de Escopo

### MVP cobre
- Autenticação local (registro, login, logout, me)
- Chat com Codex e Gemini
- Persistência de estado (`/api/state`)
- Skills customizadas por usuário
- Filesystem por usuário (CRUD completo)
- Sessão persistida em banco (sobrevive restart)

### Pós-MVP (fora do MVP)
- Live Mode (SSE/streaming para o frontend)
- STT / TTS
- `/api/exec` (execução de processos)
- `/api/system-prompts`
- Compartilhamento de tela
- Paridade total da UI atual
- Cofre de secrets

---

## 12. Critérios de Aceite

### Testes automatizados obrigatórios
- [ ] Cadastro, login, logout e `/auth/me`
- [ ] Persistência de sessão após restart
- [ ] Merge seguro de `/api/state`
- [ ] CRUD de skills por usuário (isolamento entre contas)
- [ ] Proteção contra path traversal
- [ ] Escrita, leitura, rename, delete e download de arquivos
- [ ] `POST /api/chat` com adapter mockado — codex
- [ ] `POST /api/chat` com adapter mockado — gemini

### Smoke manual do MVP
- [ ] Criar conta
- [ ] Autenticar
- [ ] Salvar estado
- [ ] Criar skill
- [ ] Criar e ler arquivo no workspace
- [ ] Enviar conversa para `codex`
- [ ] Enviar conversa para `gemini`
