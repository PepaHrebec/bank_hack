import os

import pytest
from fastapi.testclient import TestClient

from server import db, demo
from server.app import create_app
from server.orchestrator import Orchestrator


@pytest.fixture
def hub(tmp_path):
    h = demo.create_demo_app(str(tmp_path), delay=0)
    yield h
    demo.remove_david()


@pytest.fixture
def client(hub):
    with TestClient(hub) as c:
        c.get("/")
        yield c


def state(client):
    return client.get("/api/state").json()


def test_index_resets_and_injects_tour(client):
    assert client.post("/api/payments", json={"recipient": 1, "amount": 10}).status_code == 200
    page = client.get("/").text
    assert '<script src="/static/tour.js"></script>' in page
    assert '<link rel="stylesheet" href="/static/tour.css">' in page
    s = state(client)
    assert s["me"]["name"] == "David Vobecký"
    assert not any(h["kind"] == "transfer" for h in s["history"])
    assert s["friends"] == []


def test_state_does_not_reset(client):
    client.post("/api/friends", json={"account": "1111111111/0800"})
    state(client)
    assert 1 in state(client)["friends"] or state(client)["friend_requests_sent"]


def test_bot_request_endpoint(client):
    r = client.post("/api/demo/bot-request", json={"from": 3, "amount": 320, "note": "pizza"})
    assert r.status_code == 200
    [req] = state(client)["to_pay"]
    assert (req["requester"], req["amount"], req["note"]) == (3, 320, "pizza")
    assert client.post("/api/demo/bot-request", json={"from": 5, "amount": 1, "note": ""}).status_code == 400


def test_static_files_are_shared(hub):
    with TestClient(hub) as c:  # no session needed
        assert c.get("/static/tour.js").status_code == 200


def test_normal_app_has_no_demo_routes(tmp_path):
    path = str(tmp_path / "t.db")
    db.init_db(path)
    with TestClient(create_app(1, Orchestrator(), path)) as c:
        assert c.post("/api/demo/bot-request", json={"from": 3, "amount": 1}).status_code in (404, 405)
        assert "tour.js" not in c.get("/").text


def test_sessions_are_isolated(hub):
    with TestClient(hub) as a, TestClient(hub) as b:
        a.get("/")
        b.get("/")
        a.post("/api/friends", json={"account": "1111111111/0800"})
        assert state(b)["friend_requests_sent"] == [] and state(b)["friends"] == []
        b.get("/")  # B refreshing must not reset A
        s = state(a)
        assert s["friend_requests_sent"] or s["friends"]
        assert len(hub.sessions) == 2


def test_refresh_replaces_own_session(hub):
    with TestClient(hub) as a:
        a.get("/")
        a.get("/")
        assert len(hub.sessions) == 1
        assert len(os.listdir(hub.root)) == 1


def test_without_session_is_gone(hub):
    with TestClient(hub) as c:
        r = c.get("/api/state")
        assert r.status_code == 410
        assert "Obnov" in r.json()["detail"]


def test_websocket_reaches_own_session(client):
    with client.websocket_connect("/ws") as ws:
        client.post("/api/payments", json={"recipient": 1, "amount": 10})
        assert ws.receive_json()["type"] == "payment_sent"


def test_cap_drops_least_recently_used(tmp_path):
    hub = demo.create_demo_app(str(tmp_path), delay=0, max_sessions=2)
    try:
        with TestClient(hub) as a, TestClient(hub) as b, TestClient(hub) as c:
            a.get("/")
            b.get("/")
            state(a)  # a is now more recent than b
            c.get("/")
            assert b.get("/api/state").status_code == 410
            assert a.get("/api/state").status_code == 200
            assert len(hub.sessions) == 2 and len(os.listdir(tmp_path)) == 2
    finally:
        demo.remove_david()


def test_idle_sessions_are_swept(tmp_path):
    now = [1000.0]
    hub = demo.create_demo_app(str(tmp_path), delay=0, idle_secs=60, clock=lambda: now[0])
    try:
        with TestClient(hub) as a, TestClient(hub) as b:
            a.get("/")
            now[0] += 61
            b.get("/")  # a new session sweeps the idle one
            assert a.get("/api/state").status_code == 410
            assert len(hub.sessions) == 1 and len(os.listdir(tmp_path)) == 1
    finally:
        demo.remove_david()


def test_chat_and_message_limits(tmp_path):
    hub = demo.create_demo_app(str(tmp_path), delay=0, chat_limit=1, message_limit=1)
    try:
        with TestClient(hub) as c:
            c.get("/")
            ask = {"messages": [{"role": "user", "content": "ahoj"}]}
            assert c.post("/api/chat", json=ask).status_code != 429
            r = c.post("/api/chat", json=ask)
            assert r.status_code == 429 and "limit" in r.json()["detail"]
            assert c.post("/api/messages", json={"recipient": 2, "text": "ahoj"}).status_code == 200
            assert c.post("/api/messages", json={"recipient": 2, "text": "ahoj"}).status_code == 429
            c.get("/")  # a fresh session starts with fresh limits
            assert c.post("/api/messages", json={"recipient": 2, "text": "ahoj"}).status_code == 200
    finally:
        demo.remove_david()
