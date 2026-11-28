import pytest
from fastapi.testclient import TestClient

from server import db as dbm
from server.app import create_app
from server.db import (
    PaymentError, accept_friend_request, add_friend, decline_friend_request, friend_requests_by,
    friend_requests_for, friends_of, init_db, reset_db,
)
from server.orchestrator import Orchestrator
from server.seed import seed_db


@pytest.fixture
def db(tmp_path):
    path = str(tmp_path / "t.db")
    init_db(path)
    return path


def test_new_database_has_no_friends(db):
    assert all(friends_of(db, p) == [] for p in dbm.PEOPLE)


def befriend(db, a, b):
    """Make `a` and `b` friends the way the app does: a asks, b accepts."""
    add_friend(db, a, dbm.ACCOUNTS[b])
    accept_friend_request(db, b, a)


def test_init_keeps_existing_friends_and_requests(db):
    befriend(db, 1, 2)
    add_friend(db, 3, "1111111111/0800")
    init_db(db)
    assert friends_of(db, 1) == [2]
    assert friend_requests_for(db, 1) == [3]


def test_reset_and_seed_clear_friends_and_requests(db):
    befriend(db, 1, 2)
    add_friend(db, 3, "1111111111/0800")
    reset_db(db)
    assert friends_of(db, 1) == [] and friends_of(db, 2) == []
    assert friend_requests_for(db, 1) == [] and friend_requests_by(db, 3) == []
    befriend(db, 1, 2)
    add_friend(db, 3, "1111111111/0800")
    seed_db(db)
    assert all(friends_of(db, p) == [] for p in dbm.PEOPLE)
    assert all(friend_requests_for(db, p) == [] and friend_requests_by(db, p) == [] for p in dbm.PEOPLE)


def test_request_is_not_friendship(db):
    seed_db(db)
    assert add_friend(db, 1, "4444444444/0800") == (4, "requested")
    assert friends_of(db, 1) == [] and friends_of(db, 4) == []
    assert friend_requests_for(db, 4) == [1]
    assert friend_requests_by(db, 1) == [4]
    assert friend_requests_for(db, 1) == [] and friend_requests_by(db, 4) == []


def test_accept_makes_friends_both_ways(db):
    add_friend(db, 1, "4444444444/0800")
    accept_friend_request(db, 4, 1)
    assert friends_of(db, 1) == [4] and friends_of(db, 4) == [1]
    assert friend_requests_for(db, 4) == [] and friend_requests_by(db, 1) == []


def test_decline_removes_request(db):
    add_friend(db, 1, "4444444444/0800")
    decline_friend_request(db, 4, 1)
    assert friends_of(db, 1) == [] and friends_of(db, 4) == []
    assert friend_requests_for(db, 4) == [] and friend_requests_by(db, 1) == []
    assert add_friend(db, 1, "4444444444/0800") == (4, "requested")  # may ask again


def test_mutual_requests_auto_accept(db):
    add_friend(db, 1, "4444444444/0800")
    assert add_friend(db, 4, "1111111111/0800") == (1, "friends")
    assert friends_of(db, 1) == [4] and friends_of(db, 4) == [1]
    assert friend_requests_for(db, 1) == [] and friend_requests_for(db, 4) == []


@pytest.mark.parametrize("who", [accept_friend_request, decline_friend_request])
def test_answering_a_missing_request_fails(db, who):
    with pytest.raises(PaymentError, match="Žádost nebyla nalezena"):
        who(db, 4, 1)
    add_friend(db, 4, "1111111111/0800")  # only the other direction exists
    with pytest.raises(PaymentError, match="Žádost nebyla nalezena"):
        who(db, 4, 1)


def test_only_the_recipient_can_answer(db):
    add_friend(db, 1, "4444444444/0800")
    with pytest.raises(PaymentError, match="Žádost nebyla nalezena"):
        accept_friend_request(db, 1, 4)
    with pytest.raises(PaymentError, match="Žádost nebyla nalezena"):
        accept_friend_request(db, 3, 1)


@pytest.mark.parametrize("account,message", [
    ("123", "Neplatné číslo účtu"),
    ("5555555555/0800", "Přátele lze přidat jen podle účtu Geoff"),
    ("2222222222/0100", "Přátele lze přidat jen podle účtu Geoff"),
    ("5555555555/0100", "Přátele lze přidat jen podle účtu Geoff"),  # an outside contact
    ("1111111111/0800", "To je tvůj vlastní účet"),
    ("2222222222/0800", "Už jste přátelé"),
    ("3333333333/0800", "Žádost už byla odeslána"),
])
def test_add_friend_errors(db, account, message):
    befriend(db, 1, 2)
    add_friend(db, 1, "3333333333/0800")
    with pytest.raises(PaymentError, match=message):
        add_friend(db, 1, account)


def test_endpoints_and_events(db):
    seed_db(db)
    orch = Orchestrator()
    c1, c4 = (TestClient(create_app(n, orch, db)) for n in (1, 4))
    st4 = c4.get("/api/state").json()
    assert st4["friends"] == [] and st4["friend_requests"] == [] and st4["friend_requests_sent"] == []
    with c4.websocket_connect("/ws") as ws4, c1.websocket_connect("/ws") as ws1:
        r = c1.post("/api/friends", json={"account": "4444444444/0800"})
        assert r.status_code == 200
        assert r.json() == {"friend": {"id": 4, "name": "Petr Šafář", "account": "4444444444/0800", "geoff": True},
                            "status": "requested"}
        assert ws4.receive_json() == {"type": "friend_request", "from": "Štěpán Pressl", "from_id": 1,
                                      "text": "Štěpán Pressl ti posílá žádost o přátelství"}
        assert ws4.receive_json() == {"type": "friends_changed"}
        assert ws1.receive_json() == {"type": "friends_changed"}
        assert c4.get("/api/state").json()["friend_requests"] == [1]
        assert c1.get("/api/state").json()["friend_requests_sent"] == [4]
        assert c1.get("/api/state").json()["friends"] == []

        assert c4.post("/api/friends/requests/1/accept").status_code == 200
        assert ws1.receive_json() == {"type": "friend_accepted", "from": "Petr Šafář", "from_id": 4,
                                      "text": "Petr Šafář přijímá tvou žádost o přátelství"}
        assert ws1.receive_json() == {"type": "friends_changed"}
        assert ws4.receive_json() == {"type": "friends_changed"}
    st1, st4 = c1.get("/api/state").json(), c4.get("/api/state").json()
    assert st1["friends"] == [4] and st4["friends"] == [1]
    assert st1["friend_requests_sent"] == [] and st4["friend_requests"] == []


def test_mutual_request_endpoint_auto_accepts(db):
    orch = Orchestrator()
    c1, c4 = (TestClient(create_app(n, orch, db)) for n in (1, 4))
    c1.post("/api/friends", json={"account": "4444444444/0800"})
    with c1.websocket_connect("/ws") as ws1:
        r = c4.post("/api/friends", json={"account": "1111111111/0800"})
        assert r.json()["status"] == "friends"
        assert ws1.receive_json()["type"] == "friend_accepted"
    assert c1.get("/api/state").json()["friends"] == [4]


def test_decline_endpoint(db):
    orch = Orchestrator()
    c1, c4 = (TestClient(create_app(n, orch, db)) for n in (1, 4))
    c1.post("/api/friends", json={"account": "4444444444/0800"})
    with c1.websocket_connect("/ws") as ws1:
        assert c4.post("/api/friends/requests/1/decline").json() == {"ok": True}
        assert ws1.receive_json() == {"type": "friends_changed"}
    assert c1.get("/api/state").json()["friend_requests_sent"] == []
    assert c4.get("/api/state").json()["friends"] == []


def test_endpoint_errors(db):
    befriend(db, 1, 2)
    c1 = TestClient(create_app(1, Orchestrator(), db))
    assert c1.post("/api/friends", json={"account": "1111111111/0800"}).status_code == 400
    assert c1.post("/api/friends", json={"account": "2222222222/0800"}).json()["detail"] == "Už jste přátelé"
    assert c1.post("/api/friends", json={}).status_code == 400
    assert c1.post("/api/friends/requests/3/accept").json()["detail"] == "Žádost nebyla nalezena"
    assert c1.post("/api/friends/requests/3/decline").status_code == 400
