"""Read-only tools the chatbot can call: pure queries over one person's data.

`call` is the single entry point; it never raises, so a bad tool call from the model becomes an
{"error": ...} result the model can read instead of a crashed request.
"""

import unicodedata
from datetime import date, timedelta

from server import db, settle

PERIODS = ["today", "yesterday", "this_week", "last_7_days", "this_month", "last_month", "last_30_days"]
LARGEST_OUT = 5
LAST_TRANSFERS = 10
MAX_DAYS = 365


def _tool(name, description, properties=None, required=None):
    return {"type": "function", "function": {
        "name": name,
        "description": description,
        "parameters": {"type": "object", "properties": properties or {}, "required": required or []},
    }}


TOOLS = [
    _tool(
        "money_flow",
        "Shrnutí příjmů a výdajů uživatele za období: výplaty, platby kartou, převody přijaté a odeslané,"
        " celkem příchozí a odchozí, čistá změna a největší výdaje.",
        {"period": {"type": "string", "enum": PERIODS, "description": "Období (týden začíná v pondělí)."}},
        ["period"],
    ),
    _tool(
        "debts",
        "Otevřené žádosti o platbu: komu uživatel dluží (i_owe) a kdo dluží uživateli (owed_to_me).",
    ),
    _tool(
        "with_person",
        "Platby mezi uživatelem a jedním přítelem: odeslané a přijaté částky, poslední převody"
        " a otevřené dluhy v obou směrech.",
        {
            "person": {"type": "string", "description": "Jméno přítele (celé, křestní nebo příjmení)."},
            "days": {"type": "integer", "description": "Kolik dní zpět (výchozí 30)."},
        },
        ["person"],
    ),
    _tool(
        "my_groups",
        "Skupinová vyrovnání uživatele: kdo je v nich, kolik kdo zaplatil, podíl uživatele,"
        " jeho bilance a dosud nezaplacené platby vyrovnání.",
    ),
]


def period_bounds(period, today):
    """Inclusive (first, last) day of a named period; weeks start on Monday."""
    if period == "today":
        return today, today
    if period == "yesterday":
        d = today - timedelta(days=1)
        return d, d
    if period == "this_week":
        return today - timedelta(days=today.weekday()), today
    if period == "last_7_days":
        return today - timedelta(days=6), today
    if period == "this_month":
        return today.replace(day=1), today
    if period == "last_month":
        last = today.replace(day=1) - timedelta(days=1)
        return last.replace(day=1), last
    if period == "last_30_days":
        return today - timedelta(days=29), today
    raise ValueError(f"Neznámé období: {period}")


def _fold(text):
    """Lowercase without diacritics, so "Hrebec" matches "Hřebec"."""
    decomposed = unicodedata.normalize("NFD", text)
    return "".join(c for c in decomposed if not unicodedata.combining(c)).casefold().strip()


def _name(person):
    return db.PEOPLE.get(person, f"#{person}")


def money_flow(db_path, person_id, period, today):
    if period not in PERIODS:
        return {"error": f"Neznámé období. Možnosti: {', '.join(PERIODS)}"}
    first, last = period_bounds(period, today)
    income = card = transfers_in = transfers_out = count = 0
    outgoing = []
    for item in db.history(db_path, person_id):
        if not first.isoformat() <= item["created_at"][:10] <= last.isoformat():
            continue
        count += 1
        if item["kind"] == "income":
            income += item["amount"]
        elif item["kind"] == "card":
            card += item["amount"]
            outgoing.append({"kind": "card", "amount": item["amount"], "note": item["note"],
                             "created_at": item["created_at"]})
        elif item["recipient"] == person_id:
            transfers_in += item["amount"]
        else:
            transfers_out += item["amount"]
            outgoing.append({"kind": "transfer", "amount": item["amount"], "note": item["note"],
                             "person": _name(item["recipient"]), "created_at": item["created_at"]})
    outgoing.sort(key=lambda i: i["amount"], reverse=True)
    total_in, total_out = income + transfers_in, card + transfers_out
    return {
        "from": first.isoformat(), "to": last.isoformat(),
        "income": income, "card": card, "transfers_in": transfers_in, "transfers_out": transfers_out,
        "total_in": total_in, "total_out": total_out, "net": total_in - total_out,
        "count": count, "largest_out": outgoing[:LARGEST_OUT],
    }


def _group_label(group):
    return group["title"] if group else None


def debts(db_path, person_id):
    i_owe = [
        {"person": _name(r["requester"]), "amount": r["amount"], "note": r["note"], "group": _group_label(r["group"])}
        for r in db.open_requests_for(db_path, person_id)
    ]
    owed = [
        {"person": _name(r["payer"]), "amount": r["amount"], "note": r["note"], "group": _group_label(r["group"])}
        for r in db.requests_by(db_path, person_id) if r["status"] == "open"
    ]
    return {
        "i_owe": i_owe, "i_owe_total": sum(r["amount"] for r in i_owe),
        "owed_to_me": owed, "owed_to_me_total": sum(r["amount"] for r in owed),
    }


def _find_friend(person_id, query):
    """The friend id matching `query` (full, first or last name), or an error dict."""
    friends = {i: n for i, n in db.PEOPLE.items() if i != person_id}
    q = _fold(query)
    matches = [
        i for i, n in friends.items()
        if q and q in {_fold(n), _fold(n.split()[0]), _fold(n.split()[-1])}
    ]
    if len(matches) == 1:
        return matches[0], None
    if matches:
        return None, {"error": "Více kontaktů vyhovuje: " + ", ".join(friends[i] for i in matches)}
    return None, {"error": "Neznámý kontakt. Přátelé: " + ", ".join(n.split()[0] for n in friends.values())}


def with_person(db_path, person_id, person, today, days=30):
    if not isinstance(person, str):
        return {"error": "Chybí jméno přítele"}
    if type(days) is not int or not 1 <= days <= MAX_DAYS:
        return {"error": f"Počet dní musí být od 1 do {MAX_DAYS}"}
    other, error = _find_friend(person_id, person)
    if error:
        return error
    since = (today - timedelta(days=days - 1)).isoformat()
    transfers = [
        i for i in db.history(db_path, person_id)
        if i["kind"] == "transfer" and other in (i["sender"], i["recipient"]) and i["created_at"][:10] >= since
    ]
    sent = sum(t["amount"] for t in transfers if t["sender"] == person_id)
    received = sum(t["amount"] for t in transfers if t["recipient"] == person_id)
    return {
        "person": _name(other), "days": days, "sent": sent, "received": received,
        "transfers": [
            {"direction": "sent" if t["sender"] == person_id else "received",
             "amount": t["amount"], "note": t["note"], "created_at": t["created_at"]}
            for t in transfers[:LAST_TRANSFERS]
        ],
        "i_owe": sum(r["amount"] for r in db.open_requests_for(db_path, person_id) if r["requester"] == other),
        "owes_me": sum(
            r["amount"] for r in db.requests_by(db_path, person_id) if r["status"] == "open" and r["payer"] == other
        ),
    }


def my_groups(db_path, person_id):
    result = []
    with db._connect(db_path) as conn:
        for g in db.groups_for(db_path, person_id):
            paid = sum(e["amount"] for e in g["expenses"] if e["payer"] == person_id)
            share = settle.shares(g["members"], g["total"])[person_id]
            # Open requests of this group's settlement, found through the request group's link.
            unpaid = conn.execute(
                "SELECT r.payer, r.requester, r.amount FROM requests r JOIN request_groups rg"
                " ON rg.id = r.group_id WHERE rg.settle_group_id = ? AND r.status = 'open' ORDER BY r.id",
                (g["id"],),
            ).fetchall()
            result.append({
                "name": g["name"], "status": g["status"], "creator": _name(g["creator"]),
                "members": [_name(m) for m in g["members"]], "total": g["total"],
                "i_paid": paid, "my_share": share, "balance": paid - share,
                "unpaid": [{"payer": _name(u["payer"]), "payee": _name(u["requester"]), "amount": u["amount"]}
                           for u in unpaid],
            })
    return result


def call(db_path, person_id, name, args, today):
    """Run one tool by name; unknown tools and bad arguments come back as {"error": ...}."""
    try:
        if not isinstance(args, dict):
            return {"error": "Argumenty musí být objekt"}
        if name == "money_flow":
            return money_flow(db_path, person_id, args.get("period"), today)
        if name == "debts":
            return debts(db_path, person_id)
        if name == "with_person":
            return with_person(db_path, person_id, args.get("person"), today, args.get("days", 30))
        if name == "my_groups":
            return {"groups": my_groups(db_path, person_id)}
        return {"error": f"Neznámý nástroj: {name}"}
    except Exception as e:  # a tool must never take the chat down
        return {"error": f"Nástroj selhal: {e}"}
