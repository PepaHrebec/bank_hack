import pytest
from fastapi.testclient import TestClient

from server import db
from server.app import create_app
from server.orchestrator import Orchestrator


@pytest.fixture
def path(tmp_path):
    p = str(tmp_path / "t.db")
    db.init_db(p)
    return p


@pytest.mark.parametrize("text,expected", [
    ("19-2000145399/0800", "19-2000145399/0800"),
    ("2000145399/0800", "2000145399/0800"),
    ("000019-2000145399/0800", "19-2000145399/0800"),
    (" 19-2000145399 / 0800 ", "19-2000145399/0800"),
    ("000000-2000145399/0800", "2000145399/0800"),
])
def test_parse_account_valid(text, expected):
    assert db.parse_account(text) == expected


@pytest.mark.parametrize("text", [
    "19-2000145398/0800", "2000145399/800", "abc", "", "0000000000/0800",
    "1234567-2000145399/0800", "19-2/0800x", "19-20001453990/0800",
])
def test_parse_account_invalid(text):
    with pytest.raises(db.PaymentError, match="Neplatné číslo účtu"):
        db.parse_account(text)


def test_account_payment_deducts_and_is_in_history(path):
    p = db.account_payment(path, 1, "000019-2000145399/0800", 300, " nájem ")
    assert p["account"] == "19-2000145399/0800" and p["note"] == "nájem" and p["amount"] == 300
    assert set(p) == {"id", "person", "account", "amount", "note", "created_at"}
    items = db.history(path, 1)
    assert items[0]["kind"] == "account" and items[0]["account"] == "19-2000145399/0800"
    assert db.day_change(path, 1) == -300


def test_account_payment_insufficient_funds(path):
    with pytest.raises(db.PaymentError, match="Nedostatek prostředků"):
        db.account_payment(path, 1, "2000145399/0800", 10**6)
    assert db.history(path, 1) == []
    assert db.day_change(path, 1) == 0


def test_account_payment_bad_amount(path):
    with pytest.raises(db.PaymentError):
        db.account_payment(path, 1, "2000145399/0800", 0)


@pytest.fixture
def client(path):
    return TestClient(create_app(1, Orchestrator(), path))


def test_endpoint_ok(client):
    r = client.post("/api/account-payments", json={"account": "19-2000145399/0800", "amount": 100, "note": "x"})
    assert r.status_code == 200 and r.json()["account"] == "19-2000145399/0800"
    s = client.get("/api/state").json()
    assert s["balance"] == 10000 - 100 and s["history"][0]["kind"] == "account"


def test_endpoint_errors(client):
    r = client.post("/api/account-payments", json={"account": "19-2000145398/0800", "amount": 100})
    assert r.status_code == 400 and r.json()["detail"] == "Neplatné číslo účtu"
    r = client.post("/api/account-payments", json={"account": "2000145399/0800"})
    assert r.status_code == 400 and r.json()["detail"]
    r = client.post("/api/account-payments", json={"amount": 5})
    assert r.status_code == 400


def test_parse_account_rejects_non_ascii_digits():
    with pytest.raises(db.PaymentError):
        db.parse_account("١٩-2000145399/0800")
