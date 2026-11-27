import pytest

from server.db import PaymentError, get_balance, history, init_db, reset_db, send_payment


@pytest.fixture
def db(tmp_path):
    path = str(tmp_path / "t.db")
    init_db(path)
    return path


def balances(db):
    return [get_balance(db, n) for n in (1, 2, 3, 4)]


def test_starting_balances(db):
    assert balances(db) == [10000] * 4


def test_payment_moves_money(db):
    p = send_payment(db, 1, 2, 250, "lunch")
    assert p["amount"] == 250 and p["note"] == "lunch"
    assert p["sender"] == 1 and p["recipient"] == 2
    assert get_balance(db, 1) == 9750
    assert get_balance(db, 2) == 10250


def test_history_newest_first(db):
    a = send_payment(db, 1, 2, 10)
    b = send_payment(db, 3, 1, 20)
    assert [p["id"] for p in history(db, 1)] == [b["id"], a["id"]]
    assert history(db, 4) == []


def test_insufficient_funds(db):
    with pytest.raises(PaymentError):
        send_payment(db, 1, 2, 10001)
    assert balances(db) == [10000] * 4


def test_double_spend(db):
    send_payment(db, 1, 2, 6000)
    with pytest.raises(PaymentError):
        send_payment(db, 1, 3, 6000)
    assert get_balance(db, 1) == 4000


@pytest.mark.parametrize("recipient,amount", [(2, 0), (2, -5), (9, 10), (1, 10), (2, True), (2, 2.5)])
def test_invalid(db, recipient, amount):
    with pytest.raises(PaymentError):
        send_payment(db, 1, recipient, amount)
    assert balances(db) == [10000] * 4


def test_reset(db):
    send_payment(db, 1, 2, 500)
    reset_db(db)
    assert balances(db) == [10000] * 4
    assert history(db, 1) == []
