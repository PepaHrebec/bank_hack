import asyncio
import json
from datetime import date

import httpx
import pytest
from fastapi.testclient import TestClient

from server import chat, chat_tools
from server import db as server_db
from server.app import create_app
from server.db import (
    add_income, approve_group, card_payment, create_group, create_request, init_db, pay_request, send_payment,
)
from server.orchestrator import Orchestrator

TODAY = date(2026, 1, 2)
NOT_CONFIGURED = "Chat není nastavený (chybí OPENROUTER_API_KEY nebo OPENROUTER_MODEL)."
UPSTREAM = "Geoff teď neodpovídá, zkus to prosím znovu."


@pytest.fixture
def db(tmp_path):
    path = str(tmp_path / "t.db")
    init_db(path)
    return path


def at(monkeypatch, stamp):
    monkeypatch.setattr(server_db, "_now", lambda: stamp)


def test_money_flow_today(db, monkeypatch):
    at(monkeypatch, "2026-01-01T10:00:00")
    send_payment(db, 1, 2, 70, "včera")
    at(monkeypatch, "2026-01-02T09:00:00")
    send_payment(db, 1, 3, 100, "oběd")
    send_payment(db, 2, 1, 40, "zpět")
    card_payment(db, 1, 60, "káva")
    add_income(db, 1, 500, "výplata")
    r = chat_tools.call(db, 1, "money_flow", {"period": "today"}, TODAY)
    assert (r["from"], r["to"]) == ("2026-01-02", "2026-01-02")
    assert (r["income"], r["card"], r["transfers_in"], r["transfers_out"]) == (500, 60, 40, 100)
    assert (r["total_in"], r["total_out"], r["net"], r["count"]) == (540, 160, 380, 4)
    assert [i["amount"] for i in r["largest_out"]] == [100, 60]
    assert r["largest_out"][0]["person"] == "Pepa Hřebec"
    y = chat_tools.call(db, 1, "money_flow", {"period": "yesterday"}, TODAY)
    assert (y["total_out"], y["total_in"], y["count"]) == (70, 0, 1)


def test_period_bounds():
    assert chat_tools.period_bounds("this_week", TODAY) == (date(2025, 12, 29), TODAY)
    assert chat_tools.period_bounds("last_month", TODAY) == (date(2025, 12, 1), date(2025, 12, 31))
    assert chat_tools.period_bounds("last_7_days", TODAY) == (date(2025, 12, 27), TODAY)
    assert chat_tools.period_bounds("this_month", TODAY) == (date(2026, 1, 1), TODAY)


def test_debts(db):
    create_request(db, 2, 1, 100, "pizza")
    create_request(db, 1, 3, 40, "lístky")
    paid = create_request(db, 4, 1, 999, "staré")
    pay_request(db, paid["id"], 1)
    r = chat_tools.call(db, 1, "debts", {}, TODAY)
    assert r["i_owe"] == [{"person": "Jirka Měřínský", "amount": 100, "note": "pizza", "group": None}]
    assert r["i_owe_total"] == 100
    assert r["owed_to_me"][0]["person"] == "Pepa Hřebec" and r["owed_to_me_total"] == 40


def test_with_person_name_matching(db):
    send_payment(db, 1, 3, 50, "a")
    send_payment(db, 3, 1, 20, "b")
    for q in ("pepa", "Hrebec", "PEPA HŘEBEC"):
        r = chat_tools.call(db, 1, "with_person", {"person": q}, TODAY)
        assert r["person"] == "Pepa Hřebec" and (r["sent"], r["received"]) == (50, 20)
    err = chat_tools.call(db, 1, "with_person", {"person": "Karel"}, TODAY)["error"]
    assert all(n in err for n in ("Jirka", "Pepa", "Petr"))
    assert "error" in chat_tools.call(db, 1, "with_person", {"person": "Štěpán Pressl"}, TODAY)
    assert "error" in chat_tools.call(db, 1, "with_person", {"person": "Pepa", "days": "x"}, TODAY)


def test_with_person_days_window_is_inclusive_of_today(db, monkeypatch):
    # days=2 on 2026-01-02 covers Jan 1 and Jan 2 (matching last_30_days = 30 calendar days).
    at(monkeypatch, "2025-12-31T10:00:00")
    send_payment(db, 1, 3, 5, "old")
    at(monkeypatch, "2026-01-01T10:00:00")
    send_payment(db, 1, 3, 7, "edge")
    r = chat_tools.call(db, 1, "with_person", {"person": "Pepa", "days": 2}, TODAY)
    assert r["sent"] == 7


def _patched_client(monkeypatch, handler):
    real = httpx.AsyncClient
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kw: real(transport=httpx.MockTransport(handler), **kw))


def test_openrouter_from_env_request_and_reply(monkeypatch):
    seen = {}

    def handler(req):
        seen["auth"], seen["body"] = req.headers["authorization"], json.loads(req.content)
        return httpx.Response(200, json={"choices": [{"message": {"role": "assistant", "content": "Ahoj"}}]})

    _patched_client(monkeypatch, handler)
    monkeypatch.setenv("OPENROUTER_API_KEY", "k")
    monkeypatch.setenv("OPENROUTER_MODEL", "m")
    complete = chat.openrouter_from_env()
    assert asyncio.run(complete([{"role": "user", "content": "x"}], chat_tools.TOOLS))["content"] == "Ahoj"
    assert seen["auth"] == "Bearer k"
    assert seen["body"]["model"] == "m" and {"messages", "tools"} <= set(seen["body"])


def test_openrouter_thinking_off_unless_enabled(monkeypatch):
    bodies = []

    def handler(req):
        bodies.append(json.loads(req.content))
        return httpx.Response(200, json={"choices": [{"message": {"role": "assistant", "content": "Ahoj"}}]})

    _patched_client(monkeypatch, handler)
    monkeypatch.setenv("OPENROUTER_API_KEY", "k")
    monkeypatch.setenv("OPENROUTER_MODEL", "m")
    monkeypatch.delenv("OPENROUTER_REASONING", raising=False)
    asyncio.run(chat.openrouter_from_env()([], []))
    monkeypatch.setenv("OPENROUTER_REASONING", "on")
    asyncio.run(chat.openrouter_from_env()([], []))
    assert bodies[0]["reasoning"] == {"enabled": False}
    assert "reasoning" not in bodies[1]


def test_openrouter_http_error_carries_status_and_body(monkeypatch):
    _patched_client(monkeypatch, lambda req: httpx.Response(
        404, json={"error": {"message": "No endpoints found that support tool use"}}))
    monkeypatch.setenv("OPENROUTER_API_KEY", "k")
    monkeypatch.setenv("OPENROUTER_MODEL", "m")
    complete = chat.openrouter_from_env()
    with pytest.raises(chat.UpstreamError) as e:
        asyncio.run(complete([], []))
    assert "404" in str(e.value) and "support tool use" in str(e.value)


def test_openrouter_from_env_unconfigured(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.setenv("OPENROUTER_MODEL", "m")
    assert chat.openrouter_from_env() is None


def test_my_groups(db):
    g = create_group(db, 1, "Chata", [2, 3], expense={"amount": 300, "description": "nájem"}, accepted=True)
    approve_group(db, g["id"], 1)
    r = chat_tools.call(db, 2, "my_groups", {}, TODAY)["groups"]
    assert len(r) == 1 and r[0]["name"] == "Chata" and r[0]["status"] == "approved"
    assert (r[0]["i_paid"], r[0]["my_share"], r[0]["balance"], r[0]["total"]) == (0, 100, -100, 300)
    assert {"payer": "Jirka Měřínský", "payee": "Štěpán Pressl", "amount": 100} in r[0]["unpaid"]
    mine = chat_tools.call(db, 1, "my_groups", {}, TODAY)["groups"][0]
    assert (mine["i_paid"], mine["balance"]) == (300, 200)


def test_unknown_tool_returns_error(db):
    assert "error" in chat_tools.call(db, 1, "send_money", {}, TODAY)
    assert "error" in chat_tools.call(db, 1, "money_flow", {"period": "forever"}, TODAY)
    assert "error" in chat_tools.call(db, 1, "money_flow", "x", TODAY)


def tool_call(name, args="{}"):
    return {"role": "assistant", "content": None,
            "tool_calls": [{"id": "c1", "type": "function", "function": {"name": name, "arguments": args}}]}


def test_run_executes_tool_calls(db):
    create_request(db, 1, 2, 80, "x")
    seen = []

    async def complete(messages, tools):
        seen.append(list(messages))
        return tool_call("debts") if len(seen) == 1 else {"role": "assistant", "content": "Dluží ti 80 Kč."}

    reply = asyncio.run(chat.run(db, 1, [{"role": "user", "content": "Kdo mi dluží?"}], complete, TODAY))
    assert reply == "Dluží ti 80 Kč."
    assert seen[0][0]["role"] == "system" and "Štěpán Pressl" in seen[0][0]["content"]
    assert "pátek 2. 1. 2026" in seen[0][0]["content"]
    tool_msg = seen[1][-1]
    assert tool_msg["role"] == "tool" and tool_msg["tool_call_id"] == "c1"
    assert json.loads(tool_msg["content"])["owed_to_me_total"] == 80


def test_run_stops_after_5_rounds(db):
    calls = []

    async def complete(messages, tools):
        calls.append(1)
        return tool_call("debts")

    reply = asyncio.run(chat.run(db, 1, [{"role": "user", "content": "?"}], complete, TODAY))
    assert reply == "Na tohle teď nedokážu odpovědět." and len(calls) == 5


def client(db, complete=None):
    return TestClient(create_app(1, Orchestrator(), db, chat_complete=complete))


MSG = {"role": "user", "content": "Ahoj"}


def test_chat_endpoint(db):
    async def fake(messages, tools):
        return {"role": "assistant", "content": "Ahoj!"}

    c = client(db, fake)
    r = c.post("/api/chat", json={"messages": [MSG]})
    assert r.status_code == 200 and r.json() == {"reply": "Ahoj!"}
    assert c.post("/api/chat", json={"messages": [MSG] * 21}).status_code == 400
    assert c.post("/api/chat", json={"messages": [MSG, {"role": "assistant", "content": "x"}]}).status_code == 400
    assert c.post("/api/chat", json={"messages": [{"role": "user", "content": "x" * 1001}]}).status_code == 400
    assert c.post("/api/chat", json={"messages": [{"role": "system", "content": "x"}]}).status_code == 400
    assert c.post("/api/chat", json={}).status_code == 400


def test_chat_not_configured(db, monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_MODEL", raising=False)
    r = client(db).post("/api/chat", json={"messages": [MSG]})
    assert r.status_code == 503 and r.json()["detail"] == NOT_CONFIGURED


def test_chat_upstream_error(db, caplog):
    async def fake(messages, tools):
        raise chat.UpstreamError("boom")

    r = client(db, fake).post("/api/chat", json={"messages": [MSG]})
    assert r.status_code == 502 and r.json()["detail"] == UPSTREAM
    assert "boom" in caplog.text


def test_chat_deadline(db, monkeypatch):
    monkeypatch.setattr(chat, "DEADLINE", 0.05)

    async def slow(messages, tools):
        await asyncio.sleep(1)

    r = client(db, slow).post("/api/chat", json={"messages": [MSG]})
    assert r.status_code == 502 and r.json()["detail"] == UPSTREAM


@pytest.mark.parametrize("reply", [
    {"role": "assistant", "content": ["x"]},
    {"role": "assistant", "content": None, "tool_calls": "debts"},
    {"role": "assistant", "content": None, "tool_calls": ["debts"]},
    {"role": "assistant", "content": None, "tool_calls": [{"id": "1", "function": "debts"}]},
])
def test_chat_malformed_reply_is_502(db, reply):
    async def fake(messages, tools):
        return reply

    r = client(db, fake).post("/api/chat", json={"messages": [MSG]})
    assert r.status_code == 502 and r.json()["detail"] == UPSTREAM


def test_run_arguments_as_dict(db):
    n = []

    async def complete(messages, tools):
        n.append(1)
        if len(n) == 1:
            return tool_call("debts", {"x": 1})
        return {"role": "assistant", "content": "ok"}

    assert asyncio.run(chat.run(db, 1, [MSG], complete, TODAY)) == "ok"


def test_openrouter_omits_tools_key_when_empty(monkeypatch):
    bodies = []

    def handler(req):
        bodies.append(json.loads(req.content))
        return httpx.Response(200, json={"choices": [{"message": {"role": "assistant", "content": "{}"}}]})

    _patched_client(monkeypatch, handler)
    monkeypatch.setenv("OPENROUTER_API_KEY", "k")
    monkeypatch.setenv("OPENROUTER_MODEL", "m")
    complete = chat.openrouter_from_env()
    asyncio.run(complete([], []))
    asyncio.run(complete([], chat_tools.TOOLS))
    assert "tools" not in bodies[0] and "tools" in bodies[1]


def test_money_flow_counts_account_payment_as_outgoing(db, monkeypatch):
    at(monkeypatch, "2026-01-02T09:00:00")
    server_db.account_payment(db, 1, "2000145399/0800", 100)
    card_payment(db, 1, 60, "káva")
    r = chat_tools.call(db, 1, "money_flow", {"period": "today"}, TODAY)
    assert "error" not in r
    assert (r["to_accounts"], r["total_out"], r["net"], r["count"]) == (100, 160, -160, 2)
    top = r["largest_out"][0]
    assert (top["kind"], top["amount"], top["person"]) == ("account", 100, "Na účet 2000145399/0800")
    assert "error" not in chat_tools.call(db, 1, "with_person", {"person": "Pepa"}, TODAY)
