import asyncio
import json
import time

import pytest

from server import geoff_hook


@pytest.mark.parametrize("text", [
    "Pepo, dlužíš mi 300 za pivo", "rozpočítáme chatu, 4 500 za všechny", "pošli mi stovku",
    "vrať mi to prosím", "zaplatil jsem za tebe", "dáme to napůl", "rozděl to mezi nás",
    "udělejme skupinu na dovolenou", "složíme se na dárek", "máš u mě 200 Kč", "bylo to 5 litrů",
    "dej mi pětku", "dluží mi 3 koruny", "to stálo 1250", "dva tisíce korun",
])
def test_prefilter_positive(text):
    assert geoff_hook.prefilter(text)


@pytest.mark.parametrize("text", [
    "ahoj", "jdeme na pivo?", "v 8 u kina", "dobré ráno", "díky za včerejšek", "super, tak zítra",
    "kde jsi?", "Ahoj Pepo, jak se máš", "to je dobrý nápad", "", "   ",
])
def test_prefilter_negative(text):
    assert not geoff_hook.prefilter(text)


def fake(reply, calls=None):
    async def complete(messages, tools):
        if calls is not None:
            calls.append((messages, tools))
        return {"role": "assistant", "content": reply if isinstance(reply, str) else json.dumps(reply)}
    return complete


def run(text, complete, sender=1, recipient=3):
    return asyncio.run(geoff_hook.suggest(text, sender, recipient, complete))


def test_request():
    calls = []
    r = run("Pepo, dlužíš mi 300 za pivo",
            fake({"action": "request", "amount": 300, "note": "pivo", "name": None, "others": []}, calls))
    assert r == {"kind": "request", "payer": 3, "amount": 300, "note": "pivo"}
    assert calls[0][1] == [] and "Pepa" in json.dumps(calls[0][0], ensure_ascii=False)


def test_request_in_code_fence_and_noise():
    r = run("dlužíš mi 300", fake('Tady:\n```json\n{"action":"request","amount":300,"note":"x"}\n```'))
    assert r["amount"] == 300


def test_group_with_named_friend():
    r = run("rozpočítáme chatu s Jirkou, 4 500 celkem",
            fake({"action": "group", "amount": 4500, "note": "chata", "name": "Chata", "others": ["Jirka", "Jirkou?"]}))
    assert r["kind"] == "group" and r["name"] == "Chata" and r["amount"] == 4500
    assert r["members"] == [3, 2] and r["note"] == "chata"


def test_group_excludes_sender_dedups_and_defaults():
    r = run("rozdělíme to", fake({"action": "group", "amount": None, "note": "", "name": None,
                                   "others": ["Štěpán", "Pepa", "Pepa"]}))
    assert r["members"] == [3] and r["name"] == "Skupinová platba" and r["amount"] is None


def test_group_name_truncated():
    r = run("rozdělíme to", fake({"action": "group", "name": "x" * 100, "others": []}))
    assert len(r["name"]) == 40


def test_none_and_garbage():
    assert run("kolik je 5 + 5", fake({"action": "none"})) is None
    assert run("dlužíš mi 300", fake("nevím")) is None
    assert run("dlužíš mi 300", fake('{"action": "request", "amount": 3')) is None
    assert run("dlužíš mi 300", fake('[1]')) is None


@pytest.mark.parametrize("amount", [0, -5, "300", None, 12.5, True])
def test_request_bad_amount(amount):
    assert run("dlužíš mi 300", fake({"action": "request", "amount": amount, "note": "x"})) is None


def test_whole_float_amount_ok():
    assert run("dlužíš mi 300", fake({"action": "request", "amount": 300.0}))["amount"] == 300


def test_group_bad_amount_dropped_not_fatal():
    r = run("rozdělíme to", fake({"action": "group", "amount": "moc", "others": []}))
    assert r["amount"] is None


def test_prefilter_miss_never_calls():
    calls = []
    assert run("ahoj", fake({"action": "request", "amount": 5}, calls)) is None
    assert calls == []


def test_slow_complete_hits_deadline(monkeypatch):
    monkeypatch.setattr(geoff_hook, "HOOK_DEADLINE", 0.05)

    async def slow(messages, tools):
        await asyncio.sleep(2)

    t = time.monotonic()
    assert run("dlužíš mi 300", slow) is None
    assert time.monotonic() - t < 1


def test_upstream_error_and_crash_give_none():
    from server import chat

    async def boom(messages, tools):
        raise chat.UpstreamError("x")

    async def crash(messages, tools):
        raise RuntimeError("x")

    assert run("dlužíš mi 300", boom) is None
    assert run("dlužíš mi 300", crash) is None


def test_no_env_gives_none(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    assert run("dlužíš mi 300", None) is None
