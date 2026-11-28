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


@pytest.mark.parametrize("amount", [0, -5, "300", None, 12.555, True])
def test_request_bad_amount(amount):
    # No number in the text either, so the local fallback has nothing to offer.
    assert run("dlužíš mi za pivo", fake({"action": "request", "amount": amount, "note": "x"})) is None


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


@pytest.mark.parametrize("text,expected", [
    ("dal jsem 4 500", 4500), ("dal jsem 4 500 Kč", 4500), ("4500", 4500), ("celkem 4.500", 4500),
    ("300,-", 300), ("300 Kč", 300), ("300kč", 300), ("v 20:00, 300 Kč", 300),
    ("27. 11. dal jsem 250", 250), ("v 8 u kina", None), ("ahoj", None), ("200 Kč a pak 5000", 200),
])
def test_extract_amount(text, expected):
    assert geoff_hook.extract_amount(text) == expected


@pytest.mark.parametrize("text,expected", [
    ("dlužíš mi 123,50", 123.5), ("dlužíš mi 123.50", 123.5), ("bylo to 99,90 Kč", 99.9),
    ("celkem 1 234,50 Kč", 1234.5), ("celkem 4.500,25", 4500.25), ("12,50 Kč za kafe", 12.5),
    ("12.50 Kč za kafe", 12.5), ("sraz v 12.50 u kina, 300 Kč", 300), ("300,- a 120,00", 300),
])
def test_extract_decimal_amount(text, expected):
    assert geoff_hook.extract_amount(text) == expected


def test_model_decimal_amount():
    assert run("dlužíš mi 123,50", fake({"action": "request", "amount": 123.5}))["amount"] == 123.5
    # more than two decimals is not an amount; the text's own amount is used instead
    assert run("dlužíš mi 123,50", fake({"action": "request", "amount": 123.456}))["amount"] == 123.5


def test_model_null_amount_falls_back_to_text():
    r = run("rozpočítáme chatu s Jirkou, dal jsem 4 500",
            fake({"action": "group", "amount": None, "name": "Chata", "others": ["Jirka"]}))
    assert r["amount"] == 4500
    r = run("dlužíš mi 300,-", fake({"action": "request", "amount": None, "note": "x"}))
    assert r["amount"] == 300
    r = run("v 20:00, 300 Kč", fake({"action": "request", "amount": 0}))
    assert r["amount"] == 300


def test_model_amount_wins_and_no_amount_stays_none():
    assert run("dlužíš mi 300", fake({"action": "request", "amount": 250}))["amount"] == 250
    assert run("dlužíš mi něco", fake({"action": "request", "amount": None})) is None
