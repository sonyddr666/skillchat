def test_state_empty(auth_client):
    r = auth_client.get("/api/state")
    assert r.status_code == 200
    assert isinstance(r.json()["state"], dict)


def test_state_save_and_load(auth_client):
    auth_client.post("/api/state", json={"state": {"gc_theme": "dark", "gc_cfg": {"x": 1}}})
    r = auth_client.get("/api/state")
    assert r.json()["state"]["gc_theme"] == "dark"
    assert r.json()["state"]["gc_cfg"] == {"x": 1}


def test_state_only_allowed_keys(auth_client):
    auth_client.post("/api/state", json={"state": {"gc_theme": "light", "evil_key": "hacked"}})
    r = auth_client.get("/api/state")
    assert "evil_key" not in r.json()["state"]
    assert r.json()["state"]["gc_theme"] == "light"


def test_state_merge_preserves_existing(auth_client):
    auth_client.post("/api/state", json={"state": {"gc_theme": "dark"}})
    auth_client.post("/api/state", json={"state": {"gc_tts_voice": "pt-BR"}})
    r = auth_client.get("/api/state")
    assert r.json()["state"]["gc_theme"] == "dark"
    assert r.json()["state"]["gc_tts_voice"] == "pt-BR"
