import pytest

from server import db as server_db
from server.db import PaymentError, card_payment, get_balance, history, init_db, reset_db, send_payment


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


# ---- payment requests ----

from server.db import (  # noqa: E402
    create_group_request,
    create_request,
    decline_request,
    open_requests_for,
    pay_request,
)


def test_request_shows_up_for_payer(db):
    r = create_request(db, 1, 2, 250, "pizza")
    assert r["requester"] == 1 and r["payer"] == 2 and r["status"] == "open"
    todo = open_requests_for(db, 2)
    assert [t["id"] for t in todo] == [r["id"]]
    assert todo[0]["group"] is None
    assert open_requests_for(db, 1) == []
    assert balances(db) == [10000] * 4


@pytest.mark.parametrize("payer,amount", [(2, 0), (2, -1), (2, 2.5), (2, "5"), (1, 10), (9, 10)])
def test_invalid_request(db, payer, amount):
    with pytest.raises(PaymentError):
        create_request(db, 1, payer, amount)


def test_pay_request_moves_money_and_closes_it(db):
    r = create_request(db, 1, 2, 250, "pizza")
    p = pay_request(db, r["id"], 2)
    assert p["sender"] == 2 and p["recipient"] == 1 and p["amount"] == 250 and p["note"] == "pizza"
    assert get_balance(db, 1) == 10250 and get_balance(db, 2) == 9750
    assert open_requests_for(db, 2) == []
    with pytest.raises(PaymentError):
        pay_request(db, r["id"], 2)  # already paid


def test_only_payer_can_pay_or_decline(db):
    r = create_request(db, 1, 2, 250)
    with pytest.raises(PaymentError):
        pay_request(db, r["id"], 3)
    with pytest.raises(PaymentError):
        decline_request(db, r["id"], 1)
    with pytest.raises(PaymentError):
        pay_request(db, 999, 2)


def test_pay_request_insufficient_funds_keeps_it_open(db):
    r = create_request(db, 1, 2, 20000)
    with pytest.raises(PaymentError):
        pay_request(db, r["id"], 2)
    assert [t["id"] for t in open_requests_for(db, 2)] == [r["id"]]
    assert balances(db) == [10000] * 4


def test_decline_request(db):
    r = create_request(db, 1, 2, 250)
    d = decline_request(db, r["id"], 2)
    assert d["status"] == "declined"
    assert open_requests_for(db, 2) == []
    assert balances(db) == [10000] * 4


def test_group_request(db):
    g = create_group_request(db, 1, "Dinner", {2: 300, 3: 200}, "U Fleků")
    assert g["title"] == "Dinner" and g["total"] == 500
    assert sorted(r["payer"] for r in g["requests"]) == [2, 3]

    todo = open_requests_for(db, 3)
    assert len(todo) == 1 and todo[0]["amount"] == 200
    grp = todo[0]["group"]
    assert grp["title"] == "Dinner" and grp["total"] == 500
    assert {m["payer"]: m["status"] for m in grp["members"]} == {2: "open", 3: "open"}

    pay_request(db, [r for r in g["requests"] if r["payer"] == 2][0]["id"], 2)
    grp = open_requests_for(db, 3)[0]["group"]
    assert {m["payer"]: m["status"] for m in grp["members"]} == {2: "paid", 3: "open"}


@pytest.mark.parametrize("shares", [{}, {1: 100}, {2: 0}, {2: 100, 9: 50}, {2: "100"}])
def test_invalid_group_request(db, shares):
    with pytest.raises(PaymentError):
        create_group_request(db, 1, "X", shares)


def test_reset_clears_requests(db):
    create_request(db, 1, 2, 5)
    create_group_request(db, 1, "G", {3: 5})
    reset_db(db)
    assert open_requests_for(db, 2) == [] and open_requests_for(db, 3) == []


from server.db import requests_by  # noqa: E402


def test_requests_by_lists_mine_with_status(db):
    a = create_request(db, 1, 2, 100, "a")
    b = create_request(db, 1, 3, 200, "b")
    create_request(db, 2, 1, 50)  # someone else's
    g = create_group_request(db, 1, "Trip", {2: 10, 4: 20})
    pay_request(db, a["id"], 2)
    decline_request(db, b["id"], 3)

    mine = requests_by(db, 1)
    assert [r["id"] for r in mine] == [r["id"] for r in g["requests"]][::-1] + [b["id"], a["id"]]
    status = {r["id"]: r["status"] for r in mine}
    assert status[a["id"]] == "paid" and status[b["id"]] == "declined"
    assert mine[0]["group"]["title"] == "Trip"
    assert requests_by(db, 3) == []


def test_card_payment_lowers_balance_and_shows_in_history(db, monkeypatch):
    times = iter(["2026-01-01T10:00:00", "2026-01-01T10:00:01", "2026-01-01T10:00:02"])
    monkeypatch.setattr(server_db, "_now", lambda: next(times))
    a = send_payment(db, 1, 2, 10)
    c = card_payment(db, 1, 480, "  Pivnice  ")
    b = send_payment(db, 3, 1, 20)
    assert c["person"] == 1 and c["amount"] == 480 and c["note"] == "Pivnice"
    assert get_balance(db, 1) == 10000 - 10 - 480 + 20
    items = history(db, 1)
    assert [(i["kind"], i["id"]) for i in items] == [
        ("transfer", b["id"]), ("card", c["id"]), ("transfer", a["id"])]
    assert items[1] == {"kind": "card", **c}
    assert history(db, 2)[0]["kind"] == "transfer"


def test_card_payment_insufficient_funds(db):
    with pytest.raises(PaymentError, match="Insufficient funds"):
        card_payment(db, 1, 10001)
    assert balances(db) == [10000] * 4
    assert history(db, 1) == []


@pytest.mark.parametrize("amount", [0, -1, 2.5, "5", True])
def test_card_payment_invalid_amount(db, amount):
    with pytest.raises(PaymentError):
        card_payment(db, 1, amount)
    assert balances(db) == [10000] * 4


def test_card_payment_note_too_long(db):
    card_payment(db, 1, 5, "x" * 60)
    with pytest.raises(PaymentError):
        card_payment(db, 1, 5, "x" * 61)


def test_reset_clears_card_payments(db):
    card_payment(db, 1, 5)
    reset_db(db)
    assert history(db, 1) == []
    assert balances(db) == [10000] * 4
