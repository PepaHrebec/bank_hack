import pytest
from fastapi.testclient import TestClient

from server import db as dbm
from server.app import create_app
from server.db import init_db
from server.orchestrator import Orchestrator
from server.seed import seed_db


def make_clients(tmp_path, suggest):
    path = str(tmp_path / "t.db")
    init_db(path)
    orch = Orchestrator()
    return {n: TestClient(create_app(n, orch, path, suggest=suggest)) for n in (1, 2, 3, 4)}, path


async def no_suggestion(text, sender, recipient, complete=None):
    return None


@pytest.fixture
def clients(tmp_path):
    return make_clients(tmp_path, no_suggestion)[0]


def test_send_and_receive_both_directions(clients):
    with clients[2].websocket_connect("/ws") as ws2, clients[1].websocket_connect("/ws") as ws1:
        r = clients[1].post("/api/messages", json={"recipient": 2, "text": "Ahoj Jirko"})
        assert r.status_code == 200
        msg = r.json()
        assert (msg["sender"], msg["recipient"], msg["text"]) == (1, 2, "Ahoj Jirko")
        assert msg["id"] and msg["created_at"]
        for ws in (ws2, ws1):
            ev = ws.receive_json()
            assert ev == {"type": "message", "message": msg}
        r = clients[2].post("/api/messages", json={"recipient": 1, "text": "Čau"})
        assert r.status_code == 200
        assert ws1.receive_json()["message"]["text"] == "Čau"
        assert ws2.receive_json()["message"]["sender"] == 2


def test_third_person_gets_nothing(clients):
    with clients[3].websocket_connect("/ws") as ws3, clients[2].websocket_connect("/ws") as ws2:
        clients[1].post("/api/messages", json={"recipient": 2, "text": "x"})
        assert ws2.receive_json()["type"] == "message"
        clients[1].post("/api/messages", json={"recipient": 3, "text": "y"})
        assert ws3.receive_json()["message"]["text"] == "y"  # first event for 3 is its own


def test_conversation_is_oldest_first_and_private(clients):
    for sender, recipient, text in [(1, 2, "a"), (2, 1, "b"), (1, 2, "c"), (1, 3, "other")]:
        assert clients[sender].post("/api/messages", json={"recipient": recipient, "text": text}).status_code == 200
    assert [m["text"] for m in clients[1].get("/api/messages?with=2").json()] == ["a", "b", "c"]
    assert [m["text"] for m in clients[2].get("/api/messages?with=1").json()] == ["a", "b", "c"]
    assert [m["text"] for m in clients[3].get("/api/messages?with=1").json()] == ["other"]
    assert clients[4].get("/api/messages?with=1").json() == []


@pytest.mark.parametrize(
    "body",
    [
        {"recipient": 2, "text": ""},
        {"recipient": 2, "text": "   "},
        {"recipient": 2, "text": "x" * 1001},
        {"recipient": 2, "text": 5},
        {"recipient": 2},
        {"recipient": 9, "text": "ahoj"},
        {"recipient": "2", "text": "ahoj"},
        {"recipient": 1, "text": "sám sobě"},
        [1, 2],
    ],
)
def test_validation_errors(clients, body):
    r = clients[1].post("/api/messages", json=body)
    assert r.status_code == 400
    assert r.json()["detail"]
    assert clients[1].get("/api/messages?with=2").json() == []


def test_invalid_json(clients):
    r = clients[1].post("/api/messages", content=b"nope", headers={"content-type": "application/json"})
    assert r.status_code == 400


def test_max_length_text_is_ok(clients):
    assert clients[1].post("/api/messages", json={"recipient": 2, "text": "x" * 1000}).status_code == 200


@pytest.mark.parametrize("query", ["", "?with=abc", "?with=1", "?with=9"])
def test_bad_with_parameter(clients, query):
    assert clients[1].get("/api/messages" + query).status_code == 400


def test_chats_in_state(clients):
    chats = clients[1].get("/api/state").json()["chats"]
    assert [c["with"] for c in chats] == [2, 3, 4]
    assert all(c["last"] is None for c in chats)
    clients[1].post("/api/messages", json={"recipient": 3, "text": "první"})
    clients[4].post("/api/messages", json={"recipient": 1, "text": "druhá"})
    chats = clients[1].get("/api/state").json()["chats"]
    assert [c["with"] for c in chats] == [4, 3, 2]  # newest conversation first
    assert chats[0]["last"]["text"] == "druhá" and chats[0]["name"] == "Petr Šafář"
    assert chats[1]["last"]["text"] == "první"
    assert chats[2]["last"] is None


def test_db_helpers(tmp_path):
    path = str(tmp_path / "t.db")
    init_db(path)
    m = dbm.send_message(path, 1, 2, "  ahoj  ")
    assert m["text"] == "ahoj"
    assert dbm.conversation(path, 2, 1) == [m]
    for i in range(5):
        dbm.send_message(path, 2, 1, f"m{i}")
    assert [x["text"] for x in dbm.conversation(path, 1, 2, limit=3)] == ["m2", "m3", "m4"]
    with pytest.raises(dbm.PaymentError):
        dbm.send_message(path, 1, 1, "x")
    dbm.reset_db(path)
    assert dbm.conversation(path, 1, 2) == []


def test_suggestion_goes_to_sender_only(tmp_path):
    calls = []
    suggestion = {"kind": "request", "payer": 2, "amount": 300, "note": "pivo"}

    async def fake(text, sender, recipient, complete=None):
        calls.append((text, sender, recipient))
        return suggestion

    clients, _ = make_clients(tmp_path, fake)
    with clients[1].websocket_connect("/ws") as ws1, clients[1].websocket_connect("/ws") as ws1b, \
            clients[2].websocket_connect("/ws") as ws2:
        msg = clients[1].post("/api/messages", json={"recipient": 2, "text": "dlužíš mi 300"}).json()
        assert ws1.receive_json()["type"] == "message"
        assert ws2.receive_json()["type"] == "message"
        for ws in (ws1, ws1b):
            if ws is ws1b:
                assert ws.receive_json()["type"] == "message"
            ev = ws.receive_json()
            assert ev == {"type": "geoff_suggestion", "message_id": msg["id"], "suggestion": suggestion}
        # the recipient has nothing more: send another message and see that it is next
        clients[1].post("/api/messages", json={"recipient": 2, "text": "ještě"})
        assert ws2.receive_json()["message"]["text"] == "ještě"
    assert calls[0] == ("dlužíš mi 300", 1, 2)


def test_no_suggestion_when_none(tmp_path):
    clients, _ = make_clients(tmp_path, no_suggestion)
    with clients[1].websocket_connect("/ws") as ws1:
        clients[1].post("/api/messages", json={"recipient": 2, "text": "ahoj"})
        assert ws1.receive_json()["type"] == "message"
        clients[2].post("/api/messages", json={"recipient": 1, "text": "čau"})
        assert ws1.receive_json()["type"] == "message"  # next event is the reply, not a suggestion


def test_raising_suggest_still_delivers(tmp_path):
    async def boom(text, sender, recipient, complete=None):
        raise RuntimeError("kaboom")

    clients, _ = make_clients(tmp_path, boom)
    with clients[2].websocket_connect("/ws") as ws2:
        r = clients[1].post("/api/messages", json={"recipient": 2, "text": "ahoj"})
        assert r.status_code == 200
        assert ws2.receive_json()["message"]["text"] == "ahoj"
    assert len(clients[1].get("/api/messages?with=2").json()) == 1


def test_seed_has_conversations(tmp_path):
    from datetime import datetime
    path = str(tmp_path / "s.db")
    init_db(path)
    now = datetime(2026, 11, 27, 18, 30)
    seed_db(path, now=now)
    pairs = [(a, b) for a in (1, 2, 3, 4) for b in (1, 2, 3, 4) if a < b]
    for a, b in pairs:
        conv = dbm.conversation(path, a, b)
        assert 3 <= len(conv) <= 12
        assert {m["sender"] for m in conv} == {a, b}
        assert all(m["created_at"] <= now.isoformat() for m in conv)
        assert [m["created_at"] for m in conv] == sorted(m["created_at"] for m in conv)
    assert any("dlužíš" in m["text"].lower() for a, b in pairs for m in dbm.conversation(path, a, b))
    first = [dbm.conversation(path, a, b) for a, b in pairs]
    seed_db(path, now=now)
    assert [dbm.conversation(path, a, b) for a, b in pairs] == first
