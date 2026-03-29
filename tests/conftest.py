import pytest
from fastapi.testclient import TestClient
import app.config as config
import app.database as dbmod
from app.database import init_db
from app.main import app


@pytest.fixture(autouse=True)
def tmp_data(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "test.db")
    monkeypatch.setattr(config, "WORKSPACES_DIR", tmp_path / "workspaces")
    monkeypatch.setattr(config, "SKILLS_DIR", tmp_path / "skills")
    monkeypatch.setattr(config, "ATTACHMENTS_DIR", tmp_path / "attachments")
    if hasattr(dbmod._local, "conn"):
        dbmod._local.conn = None
    init_db()
    yield
    if hasattr(dbmod._local, "conn") and dbmod._local.conn:
        dbmod._local.conn.close()
        dbmod._local.conn = None


@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=True)


@pytest.fixture
def auth_client(client):
    client.post("/auth/register", json={"login": "testuser", "password": "senha123"})
    client.post("/auth/login", json={"login": "testuser", "password": "senha123"})
    return client
