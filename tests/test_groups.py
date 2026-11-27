import pytest

from server.db import (
    PaymentError,
    add_expense,
    approve_group,
    create_group,
    delete_expense,
    get_balance,
    groups_for,
    init_db,
    open_requests_for,
    requests_by,
    reset_db,
)
from server.settle import settle


@pytest.fixture
def db(tmp_path):
    path = str(tmp_path / "t.db")
    init_db(path)
    return path


def test_create_group_includes_creator_and_dedupes(db):
    g = create_group(db, 1, "  Chata  ", [2, 3, 3])
    assert g["name"] == "Chata" and g["creator"] == 1 and g["status"] == "open"
    assert sorted(g["members"]) == [1, 2, 3]
    assert [x["id"] for x in groups_for(db, 3)] == [g["id"]]
    assert groups_for(db, 4) == []


@pytest.mark.parametrize("name,members", [
    ("", [2]), ("   ", [2]), ("x" * 41, [2]), ("Chata", []), ("Chata", [1]), ("Chata", [9]),
    ("Chata", ["2"]), (5, [2]),
])
def test_invalid_group(db, name, members):
    with pytest.raises(PaymentError):
        create_group(db, 1, name, members)


def test_expenses_listed_with_total_and_no_money_moves(db):
    g = create_group(db, 1, "Chata", [2, 3])
    add_expense(db, g["id"], 1, 1200, "Cabin")
    e = add_expense(db, g["id"], 2, 300, " Food ")
    assert e["payer"] == 2 and e["description"] == "Food"
    info = groups_for(db, 3)[0]
    assert info["total"] == 1500
    assert [x["description"] for x in info["expenses"]] == ["Food", "Cabin"]
    assert [get_balance(db, n) for n in (1, 2, 3, 4)] == [10000] * 4


@pytest.mark.parametrize("amount,desc", [(0, "x"), (-5, "x"), (2.5, "x"), ("5", "x"), (5, ""), (5, "y" * 61)])
def test_invalid_expense(db, amount, desc):
    g = create_group(db, 1, "Chata", [2])
    with pytest.raises(PaymentError):
        add_expense(db, g["id"], 1, amount, desc)


def test_non_member_cannot_add(db):
    g = create_group(db, 1, "Chata", [2])
    with pytest.raises(PaymentError):
        add_expense(db, g["id"], 4, 100, "Beer")
    with pytest.raises(PaymentError):
        add_expense(db, 999, 1, 100, "Beer")


def test_delete_only_own_expense_while_open(db):
    g = create_group(db, 1, "Chata", [2])
    e = add_expense(db, g["id"], 2, 100, "Beer")
    with pytest.raises(PaymentError):
        delete_expense(db, g["id"], e["id"], 1)
    delete_expense(db, g["id"], e["id"], 2)
    assert groups_for(db, 1)[0]["expenses"] == []

    e = add_expense(db, g["id"], 2, 100, "Beer")
    approve_group(db, g["id"], 1)
    with pytest.raises(PaymentError):
        delete_expense(db, g["id"], e["id"], 2)


def test_only_creator_approves_once_and_group_locks(db):
    g = create_group(db, 1, "Chata", [2])
    with pytest.raises(PaymentError):
        approve_group(db, g["id"], 2)
    done = approve_group(db, g["id"], 1)
    assert done["status"] == "approved" and done["requests"] == []
    assert groups_for(db, 2)[0]["status"] == "approved"
    with pytest.raises(PaymentError):
        approve_group(db, g["id"], 1)
    with pytest.raises(PaymentError):
        add_expense(db, g["id"], 2, 50, "Late beer")


def test_default_split_is_empty_for_now():
    assert settle([1, 2], [{"payer": 1, "amount": 100}]) == []


def test_approve_turns_split_into_requests(db):
    g = create_group(db, 1, "Chata", [2, 3, 4])
    add_expense(db, g["id"], 1, 900, "Cabin")
    seen = {}

    def split(members, expenses):
        seen["members"], seen["expenses"] = sorted(members), [e["amount"] for e in expenses]
        return [(2, 1, 300), (3, 4, 100)]

    done = approve_group(db, g["id"], 1, split=split)
    assert seen == {"members": [1, 2, 3, 4], "expenses": [900]}
    assert sorted((r["payer"], r["requester"], r["amount"]) for r in done["requests"]) == [(2, 1, 300), (3, 4, 100)]

    todo2 = open_requests_for(db, 2)
    assert todo2[0]["amount"] == 300 and todo2[0]["requester"] == 1
    assert todo2[0]["group"]["title"] == "Chata"
    mine4 = requests_by(db, 4)
    assert [(r["payer"], r["amount"]) for r in mine4] == [(3, 100)]
    assert [get_balance(db, n) for n in (1, 2, 3, 4)] == [10000] * 4


def test_reset_clears_groups(db):
    g = create_group(db, 1, "Chata", [2])
    add_expense(db, g["id"], 1, 10, "x")
    reset_db(db)
    assert groups_for(db, 1) == []


def test_group_reports_how_many_requests_were_sent(db):
    g = create_group(db, 1, "Chata", [2, 3])
    assert groups_for(db, 3)[0]["requests_sent"] == 0
    approve_group(db, g["id"], 1, split=lambda m, e: [(2, 1, 300)])
    # Pepa is neither payer nor payee, and Jirka's request may later be paid: both still see it was sent.
    assert groups_for(db, 3)[0]["requests_sent"] == 1
    assert groups_for(db, 2)[0]["requests_sent"] == 1
