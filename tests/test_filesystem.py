def test_list_empty(auth_client):
    r = auth_client.get("/api/fs/list")
    assert r.status_code == 200


def test_write_and_read(auth_client):
    auth_client.post("/api/fs/write", json={"path": "hello.txt", "content": "mundo"})
    r = auth_client.get("/api/fs/read", params={"path": "hello.txt"})
    assert r.json()["content"] == "mundo"


def test_mkdir(auth_client):
    r = auth_client.post("/api/fs/mkdir", json={"path": "mydir"})
    assert r.status_code == 200


def test_rename(auth_client):
    auth_client.post("/api/fs/write", json={"path": "old.txt", "content": "x"})
    r = auth_client.post("/api/fs/rename", json={"path": "old.txt", "next_path": "new.txt"})
    assert r.json()["to"] == "new.txt"


def test_delete(auth_client):
    auth_client.post("/api/fs/write", json={"path": "del.txt", "content": "x"})
    r = auth_client.delete("/api/fs/delete", params={"path": "del.txt"})
    assert r.json()["ok"] is True


def test_path_traversal_blocked(auth_client):
    r = auth_client.get("/api/fs/read", params={"path": "../../etc/passwd"})
    assert r.status_code == 400


def test_download(auth_client):
    auth_client.post("/api/fs/write", json={"path": "dl.txt", "content": "baixar"})
    r = auth_client.get("/api/fs/download", params={"path": "dl.txt"})
    assert r.status_code == 200
    assert b"baixar" in r.content
