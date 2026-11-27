"""The Geoff message hook: spots money talk in a chat message and proposes a bank action.

A free local prefilter drops most messages; only the rest cost one fast model call.
`suggest` never raises and always answers within HOOK_DEADLINE seconds.
"""

import asyncio
import json
import logging
import re

from server import chat, db
from server.chat_tools import _find_friend, _fold

log = logging.getLogger("geoff.hook")

HOOK_DEADLINE = 5
DEFAULT_GROUP = "Skupinová platba"

_TIME = re.compile(r"\b\d{1,2}[:.]\d{2}\b")
_NUMBER = re.compile(r"\d{2,}")
# Folded (no diacritics, lower-case). "kc" needs word edges; the rest are stems.
_WORDS = re.compile(
    r"\bkc\b|korun|koruny|\bkorun|stovk|stokor|tisic|litr|petk|petik|dluz|vrat|posli mi|poslete mi|"
    r"zaplatil|zaplatim|za tebe|za vas|napul|rozpocit|rozdel|skupin|slozime|slozit se|prispe|"
    r"mas u me|mam u tebe|doplat|splat|vyrovn"
)

PROMPT = """\
Jsi filtr zpráv v bankovní aplikaci. Uživatel {sender} napsal zprávu příteli {recipient}.
Další přátelé: {others}.
Rozhodni, zda zpráva nabízí bankovní akci:
- "request": {sender} chce od {recipient} zaplatit konkrétní částku (např. „dlužíš mi 300 za pivo“).
- "group": zpráva navrhuje rozúčtovat / rozdělit společné výdaje mezi víc lidí.
- "none": cokoli jiného (i nejasná částka u „request“).
„note“ je jen důvod platby jedním až třemi slovy (např. „pivo“), ne opis zprávy. „name“ je krátký název
skupiny podle účelu (např. „Chata“, „Dovolená“), ne věta. Odpověz POUZE JSON bez dalšího textu:
{{"action": "none"|"request"|"group", "amount": celé číslo v Kč nebo null, "note": "krátký popis česky",
"name": "krátký název skupiny nebo null", "others": ["jména dalších přátel ve skupině"]}}"""


def prefilter(text):
    """Instant local guess: does this message look like it is about money?"""
    if not isinstance(text, str):
        return False
    t = _fold(text)
    if not t:
        return False
    return bool(_WORDS.search(t) or _NUMBER.search(_TIME.sub(" ", t)))


def _parse(content):
    if not isinstance(content, str):
        return None
    start = content.find("{")
    if start < 0:
        return None
    try:
        data, _ = json.JSONDecoder().raw_decode(content[start:])
    except ValueError:
        return None
    return data if isinstance(data, dict) else None


def _whole(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    return value if isinstance(value, int) and value > 0 else None


def _text(value, limit):
    return value.strip()[:limit] if isinstance(value, str) else ""


def _validate(data, sender, recipient):
    action = data.get("action")
    amount = _whole(data.get("amount"))
    note = _text(data.get("note"), 80)
    if action == "request":
        if amount is None:
            return None
        return {"kind": "request", "payer": recipient, "amount": amount, "note": note}
    if action == "group":
        members = [recipient]
        others = data.get("others")
        for name in others if isinstance(others, list) else []:
            if not isinstance(name, str):
                continue
            found, error = _find_friend(sender, name)
            if error is None and found not in members:
                members.append(found)
        name = _text(data.get("name"), 40) or DEFAULT_GROUP
        return {"kind": "group", "name": name, "members": members, "amount": amount, "note": note}
    return None


async def suggest(text, sender, recipient, complete=None):
    if not prefilter(text) or sender not in db.PEOPLE or recipient not in db.PEOPLE:
        return None
    try:
        complete = complete or chat.openrouter_from_env()
        if complete is None:
            return None
        system = PROMPT.format(
            sender=db.PEOPLE[sender], recipient=db.PEOPLE[recipient],
            others=", ".join(n for i, n in db.PEOPLE.items() if i not in (sender, recipient)),
        )
        messages = [{"role": "system", "content": system}, {"role": "user", "content": text}]
        reply = await asyncio.wait_for(complete(messages, []), HOOK_DEADLINE)
        data = _parse(reply.get("content") if isinstance(reply, dict) else None)
        return _validate(data, sender, recipient) if data else None
    except asyncio.TimeoutError:
        log.warning("geoff hook: model timed out after %ss", HOOK_DEADLINE)
    except chat.UpstreamError as e:
        log.warning("geoff hook: upstream failure: %s", e)
    except Exception:
        log.warning("geoff hook: unexpected failure", exc_info=True)
    return None
