from datetime import date

import pytest
from fastapi.testclient import TestClient

from server import chat_tools
from server.accounts import other_accounts
from server.app import create_app
from server.db import init_db
from server.orchestrator import Orchestrator


@pytest.mark.parametrize("person", [1, 2, 3, 4])
def test_other_accounts_kinds_and_determinism(person):
    accounts = other_accounts(person)
    assert [a["kind"] for a in accounts] == ["credit", "savings", "pension"]
    assert accounts == other_accounts(person)
    credit, savings, pension = accounts
    assert credit["name"] == "Kreditní karta" and credit["balance"] == -credit["spent"]
    assert 0 < credit["spent"] <= credit["limit"]
    assert 3 <= len(credit["transactions"]) <= 5
    assert all({"note", "amount", "date"} <= set(t) for t in credit["transactions"])
    assert savings["name"] == "Spořicí účet" and savings["balance"] > 0 and savings["rate"] > 0
    assert pension["name"] == "Penzijní spoření" and pension["monthly"] > 0 and pension["state_contribution"] > 0


def test_values_differ_per_person():
    assert len({other_accounts(p)[1]["balance"] for p in (1, 2, 3, 4)}) == 4


def test_api_accounts(tmp_path):
    db = str(tmp_path / "t.db")
    init_db(db)
    client = TestClient(create_app(2, Orchestrator(), db))
    assert client.get("/api/accounts").json() == {"accounts": other_accounts(2)}


def test_accounts_overview_tool(tmp_path):
    db = str(tmp_path / "t.db")
    init_db(db)
    r = chat_tools.call(db, 3, "accounts_overview", {}, date(2026, 1, 2))
    assert r["accounts"] == other_accounts(3)
    assert r["total"] == sum(a["balance"] for a in other_accounts(3))
    assert "accounts_overview" in [t["function"]["name"] for t in chat_tools.TOOLS]
