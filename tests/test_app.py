import asyncio

import pytest
from fastapi.testclient import TestClient

from server.app import create_app
from server.db import init_db
from server.orchestrator import Orchestrator


@pytest.fixture
def clients(tmp_path):
    db = str(tmp_path / "t.db")
    init_db(db)
    orch = Orchestrator()
    return {n: TestClient(create_app(n, orch, db)) for n in (1, 2, 3, 4)}


def test_state(clients):
    s = clients[1].get("/api/state").json()
    assert s["me"] == {"id": 1, "name": "Person 1"}
    assert s["balance"] == 10000
    assert len(s["people"]) == 4
    assert s["history"] == []


def test_payment_notifies_recipient(clients):
    with clients[2].websocket_connect("/ws") as ws2, clients[1].websocket_connect("/ws") as ws1:
        r = clients[1].post("/api/payments", json={"recipient": 2, "amount": 250, "note": "lunch"})
        assert r.status_code == 200
        ev = ws2.receive_json()
        assert ev["type"] == "payment_received"
        assert ev["text"] == "Person 1 sent you 250 CZK"
        assert ev["from"] == "Person 1"
        assert ev["payment"]["note"] == "lunch"
        assert ws1.receive_json()["type"] == "payment_sent"
    assert clients[2].get("/api/state").json()["balance"] == 10250


def test_two_tabs_same_person(clients):
    with clients[2].websocket_connect("/ws") as a, clients[2].websocket_connect("/ws") as b:
        clients[1].post("/api/payments", json={"recipient": 2, "amount": 5})
        assert a.receive_json()["type"] == "payment_received"
        assert b.receive_json()["type"] == "payment_received"


@pytest.mark.parametrize(
    "body",
    [
        {"recipient": 2, "amount": "250"},
        {"recipient": 2, "amount": 2.5},
        {"recipient": 2, "amount": 0},
        {"recipient": 2, "amount": -1},
        {"recipient": 2},
        {"recipient": "2", "amount": 5},
        {"recipient": 2, "amount": 5, "note": 7},
        [1, 2],
    ],
)
def test_bad_amounts(clients, body):
    r = clients[1].post("/api/payments", json=body)
    assert r.status_code == 400
    assert "detail" in r.json()
    assert clients[1].get("/api/state").json()["balance"] == 10000


def test_invalid_json_400(clients):
    r = clients[1].post("/api/payments", content=b"not json", headers={"content-type": "application/json"})
    assert r.status_code == 400


def test_self_payment_400(clients):
    r = clients[1].post("/api/payments", json={"recipient": 1, "amount": 5})
    assert r.status_code == 400


class DeadSocket:
    async def send_json(self, data):
        raise RuntimeError("closed")


class RecordingSocket:
    def __init__(self):
        self.got = []

    async def send_json(self, data):
        self.got.append(data)


def test_dead_socket_skipped():
    orch = Orchestrator()
    dead, rec = DeadSocket(), RecordingSocket()
    orch.sockets[2] = [dead, rec]
    asyncio.run(orch.send(2, {"type": "x"}))
    assert rec.got == [{"type": "x"}]
    assert orch.sockets[2] == [rec]


def test_index_served(clients):
    r = clients[3].get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
