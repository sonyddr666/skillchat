SKILL = {
    "name": "my_skill",
    "description": "Faz algo útil",
    "code": "print('hello')",
    "parameters": {"type": "OBJECT", "properties": {}},
}


def test_list_skills_empty(auth_client):
    r = auth_client.get("/api/skills")
    assert r.status_code == 200
    assert r.json()["skills"] == []


def test_create_and_list_skill(auth_client):
    auth_client.post("/api/skills", json=SKILL)
    r = auth_client.get("/api/skills")
    assert len(r.json()["skills"]) == 1
    assert r.json()["skills"][0]["name"] == "my_skill"


def test_delete_skill(auth_client):
    auth_client.post("/api/skills", json=SKILL)
    skills = auth_client.get("/api/skills").json()["skills"]
    skill_id = skills[0]["id"]
    r = auth_client.delete(f"/api/skills/{skill_id}")
    assert r.status_code == 200
    assert auth_client.get("/api/skills").json()["skills"] == []


def test_skills_isolated_between_users(client):
    client.post("/auth/register", json={"login": "user1", "password": "pass1111"})
    client.post("/auth/login", json={"login": "user1", "password": "pass1111"})
    client.post("/api/skills", json=SKILL)
    client.post("/auth/logout")
    client.post("/auth/register", json={"login": "user2", "password": "pass2222"})
    client.post("/auth/login", json={"login": "user2", "password": "pass2222"})
    r = client.get("/api/skills")
    assert r.json()["skills"] == []
