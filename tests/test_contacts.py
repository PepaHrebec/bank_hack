import sqlite3

import pytest
from fastapi.testclient import TestClient

from server import chat_tools, db as dbm
from server.app import create_app
from server.db import PaymentError, add_friend, contact_friends_of, init_db
from server.orchestrator import Orchestrator
from server.seed import seed_db

TIMOTHY = "5555555555/0100"


@pytest.fixture
def db(tmp_path):
    path = str(tmp_path / "t.db")
    init_db(path)
    return path


def test_known_contact():
    assert dbm.CONTACTS == {TIMOTHY: "Timothy Liška"}


def test_new_database_gives_timothy_to_everyone(db):
    assert all(contact_friends_of(db, p) == [TIMOTHY] for p in dbm.PEOPLE)


def test_migration_gives_timothy_to_everyone(tmp_path):
    path = str(tmp_path / "old.db")
    init_db(path)
    conn = sqlite3.connect(path)
    conn.execute("DROP TABLE contact_friends")
    conn.commit()
    conn.close()
    init_db(path)
    assert all(contact_friends_of(path, p) == [TIMOTHY] for p in dbm.PEOPLE)


def test_seed_gives_timothy_to_first_three(db):
    seed_db(db)
    assert [contact_friends_of(db, p) for p in (1, 2, 3, 4)] == [[TIMOTHY], [TIMOTHY], [TIMOTHY], []]


def test_add_contact_friend_and_duplicate(db):
    seed_db(db)
    assert add_friend(db, 4, "5555 555555 / 0100") == {"contact": TIMOTHY}
    assert contact_friends_of(db, 4) == [TIMOTHY]
    with pytest.raises(PaymentError, match="Už jste přátelé"):
        add_friend(db, 4, TIMOTHY)
    with pytest.raises(PaymentError, match="Tento účet nepatří uživateli Geoff"):
        add_friend(db, 4, "7777777777/0100")


def test_endpoint_contact_friend_and_state(db):
    seed_db(db)
    orch = Orchestrator()
    c4 = TestClient(create_app(4, orch, db))
    st = c4.get("/api/state").json()
    assert st["contacts"] == [{"account": TIMOTHY, "name": "Timothy Liška"}]
    assert st["contact_friends"] == []
    with c4.websocket_connect("/ws") as ws:
        r = c4.post("/api/friends", json={"account": TIMOTHY})
        assert r.status_code == 200
        assert r.json() == {"friend": {"id": None, "name": "Timothy Liška", "account": TIMOTHY, "geoff": False}}
        assert ws.receive_json() == {"type": "friends_changed"}
    assert c4.get("/api/state").json()["contact_friends"] == [TIMOTHY]
    assert c4.post("/api/friends", json={"account": TIMOTHY}).status_code == 400


def test_paying_timothy_leaves_the_app(db):
    before = {p: dbm.get_balance(db, p) for p in dbm.PEOPLE}
    p = dbm.account_payment(db, 1, TIMOTHY, 300, "kafe")
    assert "kind" not in p or p["kind"] != "transfer"
    assert dbm.get_balance(db, 1) == before[1] - 300
    assert all(dbm.get_balance(db, q) == before[q] for q in (2, 3, 4))
    assert dbm.history(db, 1)[0]["kind"] == "account"


def test_chat_breakdown_names_timothy(db):
    from datetime import date
    dbm.account_payment(db, 1, TIMOTHY, 300)
    out = chat_tools.spending_breakdown(db, 1, "today", date.today())
    assert {"label": "Pro Timothy Liška", "amount": 300} in out["items"]
