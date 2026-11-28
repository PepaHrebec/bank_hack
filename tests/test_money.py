"""Decimal money: amounts are stored in haléře (1 Kč = 100) and cross the db boundary in CZK."""

import sqlite3
from datetime import date

import pytest
from fastapi.testclient import TestClient

from server import chat_tools
from server import db as server_db
from server.app import create_app
from server.db import (
    PaymentError, add_expense, approve_group, card_payment, create_group, create_request, from_hal, get_balance,
    history, init_db, open_requests_for, pay_request, send_payment, to_hal,
)
from server.orchestrator import Orchestrator


@pytest.fixture
def db(tmp_path):
    path = str(tmp_path / "t.db")
    init_db(path)
    return path


def raw(db, sql, *args):
    conn = sqlite3.connect(db)
    try:
        return conn.execute(sql, args).fetchall()
    finally:
        conn.close()


# ---- to_hal / from_hal ----


@pytest.mark.parametrize("amount, hal", [
    (1, 100), (123, 12300), (123.45, 12345), (0.5, 50), (0.01, 1), (1.1, 110), (99.99, 9999),
    (0.1 + 0.2, 30),  # float noise far below a haléř is not a third decimal
    (19.999999999999996, 2000),
])
def test_to_hal(amount, hal):
    assert to_hal(amount) == hal
    assert type(to_hal(amount)) is int


@pytest.mark.parametrize("bad", [0, -1, -0.5, 0.0, True, False, None, "12", float("nan"), float("inf"), [1], 0.001])
def test_to_hal_rejects(bad):
    with pytest.raises(PaymentError):
        to_hal(bad)


def test_to_hal_three_decimals_message():
    with pytest.raises(PaymentError, match="nejvýš dvě desetinná místa"):
        to_hal(123.456)


def test_from_hal():
    assert from_hal(12300) == 123 and type(from_hal(12300)) is int
    assert from_hal(1250) == 12.5 and type(from_hal(1250)) is float
    assert from_hal(12345) == 123.45
    assert from_hal(1) == 0.01
    assert from_hal(0) == 0
    assert from_hal(-150) == -1.5
    for h in range(1, 100001, 7):
        assert to_hal(from_hal(h)) == h


# ---- migration ----

OLD_SCHEMA = [
    "CREATE TABLE accounts (id INTEGER PRIMARY KEY, name TEXT NOT NULL, balance INTEGER NOT NULL)",
    "CREATE TABLE payments (id INTEGER PRIMARY KEY AUTOINCREMENT, sender INTEGER NOT NULL,"
    " recipient INTEGER NOT NULL, amount INTEGER NOT NULL, note TEXT NOT NULL, created_at TEXT NOT NULL)",
    "CREATE TABLE card_payments (id INTEGER PRIMARY KEY AUTOINCREMENT, person INTEGER NOT NULL,"
    " amount INTEGER NOT NULL, note TEXT NOT NULL, created_at TEXT NOT NULL)",
    "CREATE TABLE income (id INTEGER PRIMARY KEY AUTOINCREMENT, person INTEGER NOT NULL,"
    " amount INTEGER NOT NULL, note TEXT NOT NULL, created_at TEXT NOT NULL)",
    "CREATE TABLE requests (id INTEGER PRIMARY KEY AUTOINCREMENT, group_id INTEGER,"
    " requester INTEGER NOT NULL, payer INTEGER NOT NULL, amount INTEGER NOT NULL, note TEXT NOT NULL,"
    " status TEXT NOT NULL DEFAULT 'open', payment_id INTEGER, created_at TEXT NOT NULL)",
    "CREATE TABLE settle_groups (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,"
    " creator INTEGER NOT NULL, status TEXT NOT NULL DEFAULT 'open', created_at TEXT NOT NULL, approved_at TEXT)",
    "CREATE TABLE expenses (id INTEGER PRIMARY KEY AUTOINCREMENT, group_id INTEGER NOT NULL,"
    " payer INTEGER NOT NULL, amount INTEGER NOT NULL, description TEXT NOT NULL, created_at TEXT NOT NULL)",
]


def test_migration_multiplies_old_amounts_exactly_once(tmp_path):
    path = str(tmp_path / "old.db")
    conn = sqlite3.connect(path)
    for sql in OLD_SCHEMA:
        conn.execute(sql)
    stamp = "2026-11-01T10:00:00"
    conn.executemany("INSERT INTO accounts VALUES (?, ?, ?)", [(1, "x", 9750), (2, "y", 10250), (3, "z", 10000)])
    conn.execute("INSERT INTO payments (sender, recipient, amount, note, created_at) VALUES (1, 2, 250, '', ?)", (stamp,))
    conn.execute("INSERT INTO card_payments (person, amount, note, created_at) VALUES (3, 129, 'Albert', ?)", (stamp,))
    conn.execute("INSERT INTO income (person, amount, note, created_at) VALUES (3, 129, 'Výplata', ?)", (stamp,))
    conn.execute("INSERT INTO requests (requester, payer, amount, note, created_at) VALUES (1, 2, 40, '', ?)", (stamp,))
    conn.execute("INSERT INTO settle_groups (name, creator, created_at) VALUES ('Chata', 1, ?)", (stamp,))
    conn.execute("INSERT INTO expenses (group_id, payer, amount, description, created_at) VALUES (1, 1, 900, 'x', ?)",
                 (stamp,))
    conn.commit()
    conn.close()

    init_db(path)
    init_db(path)  # a restart must not multiply again

    assert raw(path, "SELECT id, balance FROM accounts ORDER BY id") == [
        (1, 975000), (2, 1025000), (3, 1000000), (4, 1000000)]
    assert raw(path, "SELECT amount FROM payments") == [(25000,)]
    assert raw(path, "SELECT amount FROM card_payments") == [(12900,)]
    assert raw(path, "SELECT amount FROM income") == [(12900,)]
    assert raw(path, "SELECT amount FROM requests") == [(4000,)]
    assert raw(path, "SELECT amount FROM expenses") == [(90000,)]
    assert get_balance(path, 1) == 9750
    assert history(path, 1)[0]["amount"] == 250
    assert raw(path, "PRAGMA user_version") == [(server_db.SCHEMA_VERSION,)]


def test_fresh_db_starts_in_halere(db):
    init_db(db)
    assert raw(db, "SELECT balance FROM accounts") == [(1000000,)] * 4
    assert get_balance(db, 1) == 10000


# ---- decimal amounts through the db ----


def test_payment_moves_exact_halere(db):
    p = send_payment(db, 1, 2, 123.45, "oběd")
    assert p["amount"] == 123.45
    assert raw(db, "SELECT amount FROM payments") == [(12345,)]
    assert raw(db, "SELECT balance FROM accounts WHERE id IN (1, 2) ORDER BY id") == [(987655,), (1012345,)]
    assert get_balance(db, 1) == 9876.55 and get_balance(db, 2) == 10123.45
    assert history(db, 1)[0]["amount"] == 123.45 and history(db, 2)[0]["amount"] == 123.45


def test_three_decimals_rejected_and_nothing_moves(db):
    with pytest.raises(PaymentError, match="dvě desetinná"):
        send_payment(db, 1, 2, 10.005)
    assert get_balance(db, 1) == 10000 and history(db, 1) == []


def test_many_small_payments_do_not_drift(db):
    for _ in range(10):
        card_payment(db, 1, 0.1, "bonbon")
    assert get_balance(db, 1) == 9999


def test_request_of_half_a_crown(db):
    r = create_request(db, 1, 2, 0.5, "žvýkačka")
    assert r["amount"] == 0.5
    assert open_requests_for(db, 2)[0]["amount"] == 0.5
    pay_request(db, r["id"], 2)
    assert get_balance(db, 1) == 10000.5 and get_balance(db, 2) == 9999.5


def test_group_split_of_100_among_3_sums_exactly(db):
    g = create_group(db, 1, "Pizza", [2, 3], accepted=True)
    add_expense(db, g["id"], 1, 100, "pizza")
    done = approve_group(db, g["id"], 1)
    amounts = sorted((r["payer"], r["amount"]) for r in done["requests"])
    # 1 owes 33,34 Kč itself (the leftover haléř goes to the lowest id), 2 and 3 owe 33,33 Kč each.
    assert amounts == [(2, 33.33), (3, 33.33)]
    assert round(100 - sum(a for _, a in amounts), 2) == 33.34


def test_decimal_expenses_total(db):
    g = create_group(db, 1, "Výlet", [2], expense={"amount": 0.1, "description": "a"}, accepted=True)
    add_expense(db, g["id"], 2, 0.2, "b")
    from server.db import groups_for
    assert groups_for(db, 1)[0]["total"] == 0.3


# ---- endpoints and chat ----


def test_endpoint_accepts_99_99(db):
    c = TestClient(create_app(1, Orchestrator(), db))
    r = c.post("/api/payments", json={"recipient": 2, "amount": 99.99, "note": ""})
    assert r.status_code == 200 and r.json()["amount"] == 99.99
    assert c.get("/api/state").json()["balance"] == 9900.01
    bad = c.post("/api/payments", json={"recipient": 2, "amount": 1.234})
    assert bad.status_code == 400 and "dvě desetinná" in bad.json()["detail"]


def test_card_payment_endpoint_with_halere(db):
    c = TestClient(create_app(1, Orchestrator(), db))
    r = c.post("/api/card-payments", json={"amount": 59.9, "note": "Ugo"})
    assert r.status_code == 200 and r.json()["amount"] == 59.9
    assert get_balance(db, 1) == 9940.1


def test_chat_money_flow_returns_decimals(db, monkeypatch):
    monkeypatch.setattr(server_db, "_now", lambda: "2026-01-02T09:00:00")
    card_payment(db, 1, 0.1, "a")
    card_payment(db, 1, 0.2, "b")
    send_payment(db, 1, 2, 123.45, "oběd")
    r = chat_tools.call(db, 1, "money_flow", {"period": "today"}, date(2026, 1, 2))
    assert r["card"] == 0.3 and r["transfers_out"] == 123.45
    assert r["total_out"] == 123.75 and r["net"] == -123.75
    assert [i["amount"] for i in r["largest_out"]] == [123.45, 0.2, 0.1]
    b = chat_tools.call(db, 1, "spending_breakdown", {"period": "today"}, date(2026, 1, 2))
    assert b["total"] == 123.75


def test_chat_my_groups_share_in_halere(db):
    g = create_group(db, 1, "Pizza", [2, 3], accepted=True)
    add_expense(db, g["id"], 1, 100, "pizza")
    mine = chat_tools.call(db, 1, "my_groups", {}, date(2026, 1, 2))["groups"][0]
    assert (mine["total"], mine["i_paid"], mine["my_share"], mine["balance"]) == (100, 100, 33.34, 66.66)
