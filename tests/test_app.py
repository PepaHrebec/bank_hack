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
    assert s["me"] == {"id": 1, "name": "Štěpán Pressl"}
    assert s["balance"] == 10000
    assert len(s["people"]) == 4
    assert s["history"] == []


def test_payment_notifies_recipient(clients):
    with clients[2].websocket_connect("/ws") as ws2, clients[1].websocket_connect("/ws") as ws1:
        r = clients[1].post("/api/payments", json={"recipient": 2, "amount": 250, "note": "lunch"})
        assert r.status_code == 200
        ev = ws2.receive_json()
        assert ev["type"] == "payment_received"
        assert ev["text"] == "Štěpán Pressl sent you 250 CZK"
        assert ev["from"] == "Štěpán Pressl"
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


# ---- payment requests ----


def test_request_flow(clients):
    with clients[2].websocket_connect("/ws") as ws2, clients[1].websocket_connect("/ws") as ws1:
        r = clients[1].post("/api/requests", json={"payer": 2, "amount": 250, "note": "pizza"})
        assert r.status_code == 200
        rid = r.json()["id"]
        ev = ws2.receive_json()
        assert ev["type"] == "request_received"
        assert ev["text"] == "Štěpán Pressl requests 250 CZK"
        assert ws1.receive_json()["type"] == "request_sent"

        todo = clients[2].get("/api/state").json()["to_pay"]
        assert [t["id"] for t in todo] == [rid]

        r = clients[2].post(f"/api/requests/{rid}/pay")
        assert r.status_code == 200
        ev = ws1.receive_json()
        assert ev["type"] == "payment_received"
        assert ev["text"] == "Jirka Měřínský paid your request: 250 CZK"
        assert ws2.receive_json()["type"] == "payment_sent"

    assert clients[2].get("/api/state").json()["to_pay"] == []
    assert clients[1].get("/api/state").json()["balance"] == 10250


def test_decline_flow(clients):
    rid = clients[1].post("/api/requests", json={"payer": 2, "amount": 50}).json()["id"]
    with clients[1].websocket_connect("/ws") as ws1:
        assert clients[2].post(f"/api/requests/{rid}/decline").status_code == 200
        ev = ws1.receive_json()
        assert ev["type"] == "request_declined"
        assert ev["text"] == "Jirka Měřínský declined your request: 50 CZK"
    assert clients[2].get("/api/state").json()["to_pay"] == []


def test_cannot_pay_someone_elses_request(clients):
    rid = clients[1].post("/api/requests", json={"payer": 2, "amount": 50}).json()["id"]
    assert clients[3].post(f"/api/requests/{rid}/pay").status_code == 400
    assert clients[2].post("/api/requests/999/pay").status_code == 400


@pytest.mark.parametrize("body", [
    {"payer": 2, "amount": "5"}, {"payer": 2, "amount": 0}, {"payer": 1, "amount": 5},
    {"payer": "2", "amount": 5}, {"amount": 5}, {"payer": 2, "amount": 5, "note": 3}, [1],
])
def test_bad_requests(clients, body):
    r = clients[1].post("/api/requests", json=body)
    assert r.status_code == 400 and "detail" in r.json()


def test_group_request_api(clients):
    with clients[3].websocket_connect("/ws") as ws3:
        r = clients[1].post("/api/requests/group",
                            json={"title": "Dinner", "shares": {"2": 300, "3": 200}, "note": "U Fleků"})
        assert r.status_code == 200
        ev = ws3.receive_json()
        assert ev["type"] == "request_received"
        assert ev["text"] == "Štěpán Pressl requests 200 CZK for Dinner"
    todo = clients[3].get("/api/state").json()["to_pay"]
    assert todo[0]["group"]["title"] == "Dinner"


@pytest.mark.parametrize("body", [
    {"title": "X", "shares": {}}, {"title": "X", "shares": {"x": 5}}, {"title": "X", "shares": [2]},
    {"title": "X", "shares": {"2": "5"}}, {"title": 5, "shares": {"2": 5}},
])
def test_bad_group_requests(clients, body):
    assert clients[1].post("/api/requests/group", json=body).status_code == 400
