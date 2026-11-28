import pytest
from fastapi.testclient import TestClient

from server import db, demo
from server.app import create_app
from server.orchestrator import Orchestrator


@pytest.fixture
def client(tmp_path):
    app = demo.create_demo_app(str(tmp_path / "demo.db"), delay=0)
    with TestClient(app) as c:
        yield c
    demo.remove_david()


def state(client):
    return client.get("/api/state").json()


def test_index_resets_and_injects_tour(client):
    client.get("/")
    assert client.post("/api/payments", json={"recipient": 1, "amount": 10}).status_code == 200
    page = client.get("/").text
    assert '<script src="/static/tour.js"></script>' in page
    assert '<link rel="stylesheet" href="/static/tour.css">' in page
    s = state(client)
    assert s["me"]["name"] == "David Vobecký"
    assert not any(h["kind"] == "transfer" for h in s["history"])
    assert s["friends"] == []


def test_state_does_not_reset(client):
    client.get("/")
    client.post("/api/friends", json={"account": "1111111111/0800"})
    state(client)
    assert 1 in state(client)["friends"] or state(client)["friend_requests_sent"]


def test_bot_request_endpoint(client):
    client.get("/")
    r = client.post("/api/demo/bot-request", json={"from": 3, "amount": 320, "note": "pizza"})
    assert r.status_code == 200
    [req] = state(client)["to_pay"]
    assert (req["requester"], req["amount"], req["note"]) == (3, 320, "pizza")
    assert client.post("/api/demo/bot-request", json={"from": 5, "amount": 1, "note": ""}).status_code == 400


def test_normal_app_has_no_demo_routes(tmp_path):
    path = str(tmp_path / "t.db")
    db.init_db(path)
    with TestClient(create_app(1, Orchestrator(), path)) as c:
        assert c.post("/api/demo/bot-request", json={"from": 3, "amount": 1}).status_code in (404, 405)
        assert "tour.js" not in c.get("/").text
