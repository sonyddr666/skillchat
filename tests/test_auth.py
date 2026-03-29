def test_register(client):
    r = client.post("/auth/register", json={"login": "alice", "password": "abc123"})
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_login_ok(client):
    client.post("/auth/register", json={"login": "alice", "password": "abc123"})
    r = client.post("/auth/login", json={"login": "alice", "password": "abc123"})
    assert r.status_code == 200


def test_login_wrong_password(client):
    client.post("/auth/register", json={"login": "alice", "password": "abc123"})
    r = client.post("/auth/login", json={"login": "alice", "password": "wrong"})
    assert r.status_code == 401


def test_me_authenticated(auth_client):
    r = auth_client.get("/auth/me")
    assert r.status_code == 200
    assert r.json()["user"]["login"] == "testuser"


def test_me_unauthenticated(client):
    r = client.get("/auth/me")
    assert r.status_code == 401


def test_logout(auth_client):
    auth_client.post("/auth/logout")
    r = auth_client.get("/auth/me")
    assert r.status_code == 401


def test_duplicate_login(client):
    client.post("/auth/register", json={"login": "alice", "password": "abc123"})
    r = client.post("/auth/register", json={"login": "alice", "password": "xyz999"})
    assert r.status_code == 400
