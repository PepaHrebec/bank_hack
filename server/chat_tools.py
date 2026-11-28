"""Read-only tools the chatbot can call: pure queries over one person's data.

`call` is the single entry point; it never raises, so a bad tool call from the model becomes an
{"error": ...} result the model can read instead of a crashed request.
"""

import unicodedata
from datetime import date, timedelta

from server import accounts, db, settle

PERIODS = ["today", "yesterday", "this_week", "last_7_days", "this_month", "last_month", "last_30_days"]
LARGEST_OUT = 5
LAST_TRANSFERS = 10
MAX_DAYS = 365
BREAKDOWN_TOP = 7
MONTHS = ["leden", "únor", "březen", "duben", "květen", "červen", "červenec", "srpen", "září", "říjen",
          "listopad", "prosinec"]
CHART_TITLE_MAX, CHART_LABEL_MAX = 60, 30


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
    _tool(
        "accounts_overview",
        "Přehled dalších účtů uživatele: kreditní karta (limit, čerpáno, transakce), spořicí účet (zůstatek, úrok)"
        " a penzijní spoření (zůstatek, měsíční příspěvek, státní příspěvek) a součet zůstatků.",
    ),
    _tool(
        "money_series",
        "Příjmy a výdaje uživatele po týdnech nebo měsících (nejstarší první, poslední je aktuální období)."
        " Hodí se jako podklad pro čárový graf.",
        {
            "unit": {"type": "string", "enum": ["week", "month"], "description": "Délka období."},
            "count": {"type": "integer", "description": "Kolik období (2 až 12, výchozí 6)."},
        },
        ["unit"],
    ),
    _tool(
        "spending_breakdown",
        "Na co uživatel utratil peníze v období: odchozí částky podle obchodníka (karta), kamaráda a účtu,"
        " seřazené sestupně, nejmenší sloučené do Ostatní. Hodí se jako podklad pro koláčový graf.",
        {"period": {"type": "string", "enum": PERIODS, "description": "Období (týden začíná v pondělí)."}},
        ["period"],
    ),
    _tool(
        "plot_line",
        "Zobrazí uživateli čárový graf vývoje v čase (týdny, měsíce). Použij po získání čísel z datových nástrojů,"
        " když je trend lépe vidět na obrázku. Každá série má tolik hodnot, kolik je popisků.",
        {
            "title": {"type": "string", "description": "Nadpis grafu (nejvýš 60 znaků)."},
            "unit": {"type": "string", "description": "Jednotka hodnot (výchozí Kč)."},
            "labels": {"type": "array", "items": {"type": "string"}, "description": "Popisky osy x, 2 až 24."},
            "series": {
                "type": "array", "description": "1 až 3 řady.",
                "items": {"type": "object", "properties": {
                    "name": {"type": "string"},
                    "values": {"type": "array", "items": {"type": "number"}},
                }, "required": ["name", "values"]},
            },
        },
        ["title", "labels", "series"],
    ),
    _tool(
        "plot_pie",
        "Zobrazí uživateli koláčový graf podílů na celku (např. na co šly výdaje). Použij po získání čísel"
        " z datových nástrojů. 2 až 8 výřezů, hodnoty nejsou záporné.",
        {
            "title": {"type": "string", "description": "Nadpis grafu (nejvýš 60 znaků)."},
            "unit": {"type": "string", "description": "Jednotka hodnot (výchozí Kč)."},
            "labels": {"type": "array", "items": {"type": "string"}},
            "values": {"type": "array", "items": {"type": "number"}},
        },
        ["title", "labels", "values"],
    ),
]

PLOT_TOOLS = ("plot_line", "plot_pie")


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


def _flow(db_path, person_id, first, last):
    """Sums of one person's money movements between two inclusive dates (the shared counting logic)."""
    income = card = to_accounts = transfers_in = transfers_out = count = 0
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
        elif item["kind"] == "account":
            to_accounts += item["amount"]
            outgoing.append({"kind": "account", "amount": item["amount"], "note": item["note"],
                             "person": f"Na účet {item['account']}", "created_at": item["created_at"]})
        elif item["recipient"] == person_id:
            transfers_in += item["amount"]
        else:
            transfers_out += item["amount"]
            outgoing.append({"kind": "transfer", "amount": item["amount"], "note": item["note"],
                             "person": _name(item["recipient"]), "created_at": item["created_at"]})
    outgoing.sort(key=lambda i: i["amount"], reverse=True)
    total_in, total_out = income + transfers_in, card + to_accounts + transfers_out
    return {
        "from": first.isoformat(), "to": last.isoformat(),
        "income": income, "card": card, "to_accounts": to_accounts, "transfers_in": transfers_in, "transfers_out": transfers_out,
        "total_in": total_in, "total_out": total_out, "net": total_in - total_out,
        "count": count, "outgoing": outgoing,
    }


def money_flow(db_path, person_id, period, today):
    if period not in PERIODS:
        return {"error": f"Neznámé období. Možnosti: {', '.join(PERIODS)}"}
    flow = _flow(db_path, person_id, *period_bounds(period, today))
    outgoing = flow.pop("outgoing")
    flow["largest_out"] = outgoing[:LARGEST_OUT]
    return flow


def _bucket_bounds(unit, count, today):
    """Inclusive (first, last, label) per bucket, oldest first, ending with the current week/month."""
    out = []
    if unit == "week":
        monday = today - timedelta(days=today.weekday())
        for i in range(count - 1, -1, -1):
            first = monday - timedelta(weeks=i)
            out.append((first, min(first + timedelta(days=6), today), f"{first.day}. {first.month}."))
    else:
        for i in range(count - 1, -1, -1):
            idx = today.year * 12 + today.month - 1 - i
            year, month = divmod(idx, 12)
            first = date(year, month + 1, 1)
            last = min((first + timedelta(days=31)).replace(day=1) - timedelta(days=1), today)
            label = MONTHS[month] + ("" if year == today.year else f" {year}")
            out.append((first, last, label))
    return out


def money_series(db_path, person_id, unit, count, today):
    if unit not in ("week", "month"):
        return {"error": "Jednotka musí být week nebo month"}
    if type(count) is not int or not 2 <= count <= 12:
        return {"error": "Počet období musí být od 2 do 12"}
    keys = ("income", "card", "to_accounts", "transfers_in", "transfers_out", "total_in", "total_out", "net")
    buckets = []
    for first, last, label in _bucket_bounds(unit, count, today):
        flow = _flow(db_path, person_id, first, last)
        buckets.append({"label": label, "from": flow["from"], "to": flow["to"], **{k: flow[k] for k in keys}})
    return {"unit": unit, "buckets": buckets}


def spending_breakdown(db_path, person_id, period, today):
    if period not in PERIODS:
        return {"error": f"Neznámé období. Možnosti: {', '.join(PERIODS)}"}
    flow = _flow(db_path, person_id, *period_bounds(period, today))
    sums = {}
    for o in flow["outgoing"]:
        if o["kind"] == "card":
            label = o["note"] or "Platba kartou"
        elif o["kind"] == "account":
            label = o["person"]
        else:
            label = f"Převod: {o['person'].split()[0]}"
        sums[label] = sums.get(label, 0) + o["amount"]
    items = sorted(({"label": k, "amount": v} for k, v in sums.items()), key=lambda i: (-i["amount"], i["label"]))
    if len(items) > BREAKDOWN_TOP + 1:
        rest = sum(i["amount"] for i in items[BREAKDOWN_TOP:])
        items = items[:BREAKDOWN_TOP] + [{"label": "Ostatní", "amount": rest}]
    return {"from": flow["from"], "to": flow["to"], "total": flow["total_out"], "items": items}


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


def _is_num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and x == x and abs(x) != float("inf")


def _text(x, limit, what):
    if not isinstance(x, str) or not x.strip():
        return None, f"{what} musí být neprázdný text"
    if len(x) > limit:
        return None, f"{what} může mít nejvýš {limit} znaků"
    return x, None


def _labels(raw, lo, hi):
    if not isinstance(raw, list) or not lo <= len(raw) <= hi:
        return None, f"Popisků musí být {lo} až {hi}"
    for label in raw:
        _, err = _text(label, CHART_LABEL_MAX, "Popisek")
        if err:
            return None, err
    return list(raw), None


def _numbers(raw, n, what):
    if not isinstance(raw, list) or len(raw) != n or not all(_is_num(v) for v in raw):
        return None, f"{what} musí obsahovat {n} čísel"
    return list(raw), None


def chart(name, args):
    """Validate a plot tool call: (spec, result_for_model); spec is None when invalid."""
    def bad(msg):
        return None, {"error": msg}

    if not isinstance(args, dict):
        return bad("Argumenty musí být objekt")
    title, err = _text(args.get("title"), CHART_TITLE_MAX, "Nadpis")
    if err:
        return bad(err)
    unit = args.get("unit", "Kč")
    if unit is None:
        unit = "Kč"
    unit, err = _text(unit, 10, "Jednotka")
    if err:
        return bad(err)
    if name == "plot_pie":
        labels, err = _labels(args.get("labels"), 2, 8)
        if err:
            return bad(err)
        values, err = _numbers(args.get("values"), len(labels), "Hodnoty")
        if err:
            return bad(err)
        if any(v < 0 for v in values) or sum(values) <= 0:
            return bad("Hodnoty koláče nesmí být záporné a jejich součet musí být kladný")
        spec = {"type": "pie", "title": title, "unit": unit, "labels": labels, "values": values}
    elif name == "plot_line":
        labels, err = _labels(args.get("labels"), 2, 24)
        if err:
            return bad(err)
        raw = args.get("series")
        if not isinstance(raw, list) or not 1 <= len(raw) <= 3 or not all(isinstance(s, dict) for s in raw):
            return bad("Řad musí být 1 až 3")
        series = []
        for s in raw:
            sname, err = _text(s.get("name"), CHART_LABEL_MAX, "Název řady")
            if err:
                return bad(err)
            values, err = _numbers(s.get("values"), len(labels), f"Řada „{sname}“")
            if err:
                return bad(err)
            series.append({"name": sname, "values": values})
        spec = {"type": "line", "title": title, "unit": unit, "labels": labels, "series": series}
    else:
        return bad(f"Neznámý graf: {name}")
    return spec, {"ok": True, "shown": "graf je zobrazen uživateli"}


def call(db_path, person_id, name, args, today):
    """Run one tool by name; unknown tools and bad arguments come back as {"error": ...}."""
    try:
        if not isinstance(args, dict):
            return {"error": "Argumenty musí být objekt"}
        if name == "money_flow":
            return money_flow(db_path, person_id, args.get("period"), today)
        if name == "money_series":
            return money_series(db_path, person_id, args.get("unit"), args.get("count", 6), today)
        if name == "spending_breakdown":
            return spending_breakdown(db_path, person_id, args.get("period"), today)
        if name == "debts":
            return debts(db_path, person_id)
        if name == "with_person":
            return with_person(db_path, person_id, args.get("person"), today, args.get("days", 30))
        if name == "my_groups":
            return {"groups": my_groups(db_path, person_id)}
        if name == "accounts_overview":
            items = accounts.other_accounts(person_id)
            return {"accounts": items, "total": sum(a["balance"] for a in items)}
        return {"error": f"Neznámý nástroj: {name}"}
    except Exception as e:  # a tool must never take the chat down
        return {"error": f"Nástroj selhal: {e}"}
