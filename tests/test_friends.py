import sqlite3

import pytest
from fastapi.testclient import TestClient

from server import db as dbm
from server.app import create_app
from server.db import PaymentError, add_friend, friends_of, init_db, reset_db
from server.orchestrator import Orchestrator
from server.seed import seed_db


@pytest.fixture
def db(tmp_path):
    path = str(tmp_path / "t.db")
    init_db(path)
    return path


def test_new_database_has_all_pairs(db):
    assert friends_of(db, 1) == [2, 3, 4]
    assert friends_of(db, 4) == [1, 2, 3]


def test_migration_of_old_database_gives_all_pairs(tmp_path):
    path = str(tmp_path / "old.db")
    init_db(path)
    conn = sqlite3.connect(path)
    conn.execute("DROP TABLE friends")
    conn.commit()
    conn.close()
    init_db(path)
    assert all(friends_of(path, p) == [q for q in dbm.PEOPLE if q != p] for p in dbm.PEOPLE)


def test_init_does_not_restore_removed_friends(db):
    dbm.clear_friends(db, 4)
    init_db(db)
    assert friends_of(db, 4) == []


def test_reset_keeps_pairs(db):
    reset_db(db)
    assert friends_of(db, 2) == [1, 3, 4]


def test_seed_leaves_petr_without_friends(db):
    seed_db(db)
    assert friends_of(db, 4) == []
    assert friends_of(db, 1) == [2, 3]
    assert friends_of(db, 2) == [1, 3]


def test_seed_rebuilds_friends_regardless_of_previous_state(db):
    seed_db(db)
    add_friend(db, 1, "4444444444/0800")
    dbm.clear_friends(db, 2)
    seed_db(db)
    assert [friends_of(db, p) for p in (1, 2, 3, 4)] == [[2, 3], [1, 3], [1, 2], []]


def test_add_friend_both_ways(db):
    seed_db(db)
    assert add_friend(db, 1, "4444444444/0800") == 4
    assert friends_of(db, 1) == [2, 3, 4]
    assert friends_of(db, 4) == [1]


@pytest.mark.parametrize("account,message", [
    ("123", "Neplatné číslo účtu"),
    ("5555555555/0800", "Tento účet nepatří uživateli Geoff"),
    ("2222222222/0100", "Tento účet nepatří uživateli Geoff"),
    ("1111111111/0800", "To je tvůj vlastní účet"),
    ("2222222222/0800", "Už jste přátelé"),
])
def test_add_friend_errors(db, account, message):
    seed_db(db)
    with pytest.raises(PaymentError, match=message):
        add_friend(db, 1, account)


def test_endpoint_and_events(db):
    seed_db(db)
    orch = Orchestrator()
    c1, c4 = (TestClient(create_app(n, orch, db)) for n in (1, 4))
    assert c4.get("/api/state").json()["friends"] == []
    with c4.websocket_connect("/ws") as ws4, c1.websocket_connect("/ws") as ws1:
        r = c1.post("/api/friends", json={"account": "4444444444/0800"})
        assert r.status_code == 200
        assert r.json() == {"friend": {"id": 4, "name": "Petr Šafář", "account": "4444444444/0800"}}
        added = ws4.receive_json()
        assert added == {"type": "friend_added", "from": "Štěpán Pressl", "from_id": 1,
                         "text": "Štěpán Pressl si tě přidává mezi přátele"}
        assert ws4.receive_json() == {"type": "friends_changed"}
        assert ws1.receive_json() == {"type": "friends_changed"}
    assert c4.get("/api/state").json()["friends"] == [1]
    assert c1.get("/api/state").json()["friends"] == [2, 3, 4]


def test_endpoint_errors(db):
    c1 = TestClient(create_app(1, Orchestrator(), db))
    assert c1.post("/api/friends", json={"account": "1111111111/0800"}).status_code == 400
    assert c1.post("/api/friends", json={"account": "2222222222/0800"}).json()["detail"] == "Už jste přátelé"
    assert c1.post("/api/friends", json={}).status_code == 400
