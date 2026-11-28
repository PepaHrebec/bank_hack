from datetime import datetime

import pytest

from server.db import (
    START_BALANCE,
    get_balance,
    groups_for,
    history,
    init_db,
    open_requests_for,
    send_payment,
    to_hal,
)
from server.seed import seed_db

NOW = datetime(2026, 11, 27, 18, 30)


@pytest.fixture
def db(tmp_path):
    path = str(tmp_path / "t.db")
    init_db(path)
    return path


@pytest.fixture
def seeded(db):
    counts = seed_db(db, now=NOW)
    return db, counts


def test_everyone_has_at_least_200_payments(seeded):
    db, counts = seeded
    for p in (1, 2, 3, 4):
        assert len(history(db, p)) >= 200
        assert counts[p] == len(history(db, p))


def test_about_30_percent_are_friend_transfers(seeded):
    db, _ = seeded
    for p in (1, 2, 3, 4):
        items = history(db, p)
        transfers = [i for i in items if i["kind"] == "transfer"]
        assert 0.25 <= len(transfers) / len(items) <= 0.35


def test_card_notes_are_czech_businesses(seeded):
    db, _ = seeded
    notes = set()
    for p in (1, 2, 3, 4):
        for i in history(db, p):
            if i["kind"] == "card":
                assert i["note"]
                notes.add(i["note"])
    assert len(notes) >= 25


def test_monthly_salary(seeded):
    db, _ = seeded
    for p in (1, 2, 3, 4):
        salaries = [i for i in history(db, p) if i["kind"] == "income"]
        assert len(salaries) == 3
        assert all(i["note"] == "Výplata" for i in salaries)


def test_balances_consistent_and_never_negative(seeded):
    db, _ = seeded
    for p in (1, 2, 3, 4):
        balance = to_hal(START_BALANCE)  # summed in haléře, so decimal amounts add up exactly
        for i in reversed(history(db, p)):
            incoming = i["kind"] == "income" or (i["kind"] == "transfer" and i["recipient"] == p)
            balance += to_hal(i["amount"]) if incoming else -to_hal(i["amount"])
            assert balance >= 0
        assert balance == to_hal(get_balance(db, p))


def test_nothing_in_the_future_and_some_today(seeded):
    db, _ = seeded
    for p in (1, 2, 3, 4):
        items = history(db, p)
        assert all(i["created_at"] <= NOW.isoformat() for i in items)
        today = [i for i in items if i["created_at"][:10] == NOW.date().isoformat()]
        assert len(today) >= 2


def test_open_requests_and_group(seeded):
    db, _ = seeded
    assert sum(1 for p in (1, 2, 3, 4) if open_requests_for(db, p)) >= 2
    groups = [g for g in groups_for(db, 1) if g["status"] == "open" and g["creator"] != 1]
    assert groups and len(groups[0]["expenses"]) >= 2


def test_deterministic_and_wipes_first(db):
    seed_db(db, now=NOW)
    first = history(db, 1)
    send_payment(db, 1, 2, 5, "stará platba")
    seed_db(db, now=NOW)
    assert history(db, 1) == first
