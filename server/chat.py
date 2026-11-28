"""The Geoff chatbot: a tool-calling loop over an OpenAI-compatible chat API (OpenRouter).

The model only ever sees data through the read-only tools in `chat_tools`; it cannot move money.
"""

import asyncio
import json
import os
from datetime import date

import httpx

from server import chat_tools, db

MAX_ROUNDS = 5
FALLBACK = "Na tohle teď nedokážu odpovědět."
URL = "https://openrouter.ai/api/v1/chat/completions"
TIMEOUT = 30
DEADLINE = 60  # total seconds for one chat request, however many rounds it takes
WEEKDAYS = ["pondělí", "úterý", "středa", "čtvrtek", "pátek", "sobota", "neděle"]

SYSTEM_PROMPT = """\
Jsi Geoff, asistent v bankovní aplikaci Geoff. Mluvíš s uživatelem {name}. Dnes je {weekday} {date}.
Přátelé uživatele: {friends}.
Odpovídej vždy česky, stručně (nejvýš pár řádků), částky piš vždy se dvěma desetinnými místy jako „1 234,50 Kč“ (nástroje vrací částky v Kč, 123.5 je 123,50 Kč). Tykej a piš genderově neutrálně:
ne „utratil(a) jsi“, ale třeba „utratilo se“, „odešlo“, „šlo na“.
Čísla ber jen z nástrojů, nic si nevymýšlej. Umíš: shrnout platby za období, říct, kdo komu dluží (otevřené žádosti),
ukázat platby s jedním přítelem, stav skupinových vyrovnání a přehled dalších účtů (kreditní karta, spořicí účet, penzijní spoření). Peníze posílat ani žádosti platit neumíš.
Umíš nakreslit graf: čárový (plot_line) pro vývoj v čase a koláčový (plot_pie) pro podíly na celku. Graf nakresli,
když o něj uživatel požádá nebo když je trend či rozdělení na obrázku srozumitelnější. Nejdřív získej čísla z datových
nástrojů (money_series, spending_breakdown), potom zavolej plot nástroj a v textu odpověz stručně, bez opakování všech čísel. Graf aplikace ukáže sama, nepiš, kde je (ani „výše“, ani „níže“).
O dalších účtech uživatele (kreditní karta, spořicí účet, penzijní spoření) řekni přes accounts_overview.
Na jiné otázky odpověz, že s tím nepomůžeš, a nabídni, co umíš."""


class UpstreamError(Exception):
    """The model provider failed or answered something we can't read."""


def system_prompt(person_id, today):
    friends = ", ".join(n for i, n in db.PEOPLE.items() if i != person_id)
    return SYSTEM_PROMPT.format(
        name=db.PEOPLE[person_id], weekday=WEEKDAYS[today.weekday()],
        date=f"{today.day}. {today.month}. {today.year}", friends=friends,
    )


async def run(db_path, person_id, messages, complete, today=None, charts=None):
    today = today or date.today()
    convo = [{"role": "system", "content": system_prompt(person_id, today)}, *messages]
    for _ in range(MAX_ROUNDS):
        reply = await complete(convo, chat_tools.TOOLS)
        if not isinstance(reply, dict):
            raise UpstreamError("Unexpected reply shape")
        calls = reply.get("tool_calls")
        if not calls:
            content = reply.get("content")
            if content is not None and not isinstance(content, str):
                raise UpstreamError("Unexpected content shape")
            return content or FALLBACK
        if not isinstance(calls, list) or not all(isinstance(c, dict) for c in calls):
            raise UpstreamError("Unexpected tool_calls shape")
        convo.append(reply)
        for c in calls:
            fn = c.get("function")
            if not isinstance(fn, dict):
                raise UpstreamError("Unexpected tool call shape")
            args = fn.get("arguments") or "{}"
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except ValueError:
                    args = None
            if not isinstance(args, dict):
                result = {"error": "Neplatné argumenty nástroje"}
            elif fn.get("name") in chat_tools.PLOT_TOOLS:
                spec, result = chat_tools.chart(fn["name"], args)
                if spec is not None and charts is not None:
                    charts.append(spec)
            else:
                result = await asyncio.to_thread(
                    chat_tools.call, db_path, person_id, fn.get("name"), args, today
                )
            convo.append({"role": "tool", "tool_call_id": c.get("id"),
                          "content": json.dumps(result, ensure_ascii=False)})
    return FALLBACK


def openrouter_from_env():
    """An async `complete` for OpenRouter, or None when the key or model isn't configured."""
    key, model = os.environ.get("OPENROUTER_API_KEY"), os.environ.get("OPENROUTER_MODEL")
    if not key or not model:
        return None
    body = {"model": model}
    if os.environ.get("OPENROUTER_REASONING", "").lower() not in ("on", "1", "true"):
        # Hidden "thinking" tokens made answers 3-4x slower without making them better.
        body["reasoning"] = {"enabled": False}

    async def complete(messages, tools):
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                payload = {**body, "messages": messages}
                if tools:  # a plain classification call has no tools; an empty list is invalid
                    payload["tools"] = tools
                r = await client.post(URL, headers={"Authorization": f"Bearer {key}"}, json=payload)
            r.raise_for_status()
            message = r.json()["choices"][0]["message"]
        except httpx.HTTPStatusError as e:
            # OpenRouter explains misconfiguration (bad model, no tool support) in the body.
            raise UpstreamError(f"HTTP {e.response.status_code}: {e.response.text[:300]}") from e
        except (httpx.HTTPError, ValueError, KeyError, IndexError, TypeError) as e:
            raise UpstreamError(str(e) or type(e).__name__) from e
        if not isinstance(message, dict):
            raise UpstreamError("Unexpected response shape")
        return message

    return complete
