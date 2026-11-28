from datetime import datetime

import pytest

from server import db, demo

NOW = datetime(2026, 11, 28, 12, 0)


@pytest.fixture
def path(tmp_path):
    demo.add_david()
    p = str(tmp_path / "d.db")
    db.init_db(p)
    yield p
    demo.remove_david()


def test_add_david_idempotent():
    demo.add_david()
    demo.add_david()
    try:
        assert db.PEOPLE[5] == "David Vobecký"
        assert db.ACCOUNTS[5] == "5555555555/0800"
        assert db.person_by_account("5555555555/0800") == 5
        assert db.person_by_account("5555555555/0100") is None
    finally:
        demo.remove_david()
    assert 5 not in db.PEOPLE and 5 not in db.ACCOUNTS


def test_seed_gives_david_history_only(path):
    demo.seed_demo(path, now=NOW)
    h = db.history(path, 5)
    assert len(h) > 50
    assert any(x.get("note") == "Výplata" for x in h)
    for p in (1, 2, 3, 4):
        assert db.history(path, p) == []
        assert db.get_balance(path, p) == db.START_BALANCE
    assert db.friends_of(path, 5) == []
    assert db.groups_for(path, 5) == [] and db.open_requests_for(path, 5) == []
    assert db.conversation(path, 5, 2)


def test_seed_twice_is_identical(path):
    demo.seed_demo(path, now=NOW)
    first = db.history(path, 5)
    db.send_payment(path, 5, 1, 10)
    demo.seed_demo(path, now=NOW)
    assert db.history(path, 5) == first
