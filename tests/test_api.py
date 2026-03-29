"""Integration tests for the Retail Chat Agent FastAPI application."""

import pytest


@pytest.mark.unit
def test_healthcheck(client):
    resp = client.get("/api/v1/healthcheck")
    assert resp.status_code == 200
    assert resp.json() == {"Backend Status": "Ready"}


@pytest.mark.unit
def test_chat_creates_new_session(client):
    resp = client.post("/api/v1/chat", json={"message": "blue running shoes"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["response"] == "Here are some matching products!"
    assert data["session_id"] is not None


@pytest.mark.unit
def test_chat_uses_provided_session_id(client):
    resp = client.post("/api/v1/chat", json={"message": "leather handbag", "session_id": "my-sess"})
    assert resp.status_code == 200
    assert resp.json()["session_id"] == "my-sess"


@pytest.mark.unit
def test_chat_with_image(client):
    resp = client.post(
        "/api/v1/chat",
        json={
            "message": "find this product",
            "image_b64": "aGVsbG8=",
            "session_id": "img-sess",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["session_id"] == "img-sess"


@pytest.mark.unit
def test_chat_persists_history(client):
    client.post(
        "/api/v1/chat",
        json={"message": "red jacket", "session_id": "hist-test"},
    )
    resp = client.post(
        "/api/v1/chat",
        json={"message": "anything cheaper?", "session_id": "hist-test"},
    )
    assert resp.status_code == 200


@pytest.mark.unit
def test_sessions_empty(client):
    resp = client.get("/api/v1/sessions")
    assert resp.status_code == 200
    assert resp.json() == {"sessions": []}


@pytest.mark.unit
def test_sessions_lists_after_chat(client):
    client.post("/api/v1/chat", json={"message": "hello", "session_id": "list-me"})
    resp = client.get("/api/v1/sessions")
    assert "list-me" in resp.json()["sessions"]


@pytest.mark.unit
def test_session_history_returns_messages(client):
    client.post(
        "/api/v1/chat",
        json={"message": "summer dress", "session_id": "history-sid"},
    )
    resp = client.get("/api/v1/sessions/history-sid")
    assert resp.status_code == 200
    data = resp.json()
    assert data["session_id"] == "history-sid"
    assert len(data["messages"]) == 2


@pytest.mark.unit
def test_session_history_not_found(client):
    resp = client.get("/api/v1/sessions/nonexistent-session")
    assert resp.status_code == 404


@pytest.mark.unit
def test_delete_session(client):
    client.post("/api/v1/chat", json={"message": "hello", "session_id": "del-me"})
    resp = client.delete("/api/v1/sessions/del-me")
    assert resp.status_code == 204
    assert client.get("/api/v1/sessions/del-me").status_code == 404


@pytest.mark.unit
def test_delete_nonexistent_session(client):
    resp = client.delete("/api/v1/sessions/ghost-session")
    assert resp.status_code == 404
