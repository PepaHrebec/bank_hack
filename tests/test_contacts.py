import pytest
from fastapi.testclient import TestClient

from server import chat_tools, db as dbm
from server.app import create_app
from server.db import PaymentError, add_friend, init_db
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


def test_contact_cannot_be_befriended(db):
    with pytest.raises(PaymentError, match="Přátele lze přidat jen podle účtu Geoff"):
        add_friend(db, 4, TIMOTHY)


def test_state_lists_contacts_but_no_contact_friends(db):
    st = TestClient(create_app(4, Orchestrator(), db)).get("/api/state").json()
    assert st["contacts"] == [{"account": TIMOTHY, "name": "Timothy Liška"}]
    assert "contact_friends" not in st
    r = TestClient(create_app(4, Orchestrator(), db)).post("/api/friends", json={"account": TIMOTHY})
    assert r.status_code == 400


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
