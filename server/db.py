"""SQLite storage for the payments and payment requests of the four mockup people."""

import sqlite3
from contextlib import contextmanager
from datetime import datetime

from server import settle as split_slot

PEOPLE = {1: "Štěpán Pressl", 2: "Jirka Měřínský", 3: "Pepa Hřebec", 4: "Petr Šafář"}
START_BALANCE = 10000


class PaymentError(Exception):
    pass


@contextmanager
def _connect(path):
    # Autocommit mode; multi-statement writes use explicit BEGIN IMMEDIATE.
    conn = sqlite3.connect(path, timeout=5, isolation_level=None)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db(path):
    with _connect(path) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS accounts ("
            " id INTEGER PRIMARY KEY, name TEXT NOT NULL, balance INTEGER NOT NULL)"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS payments ("
            " id INTEGER PRIMARY KEY AUTOINCREMENT,"
            " sender INTEGER NOT NULL, recipient INTEGER NOT NULL,"
            " amount INTEGER NOT NULL, note TEXT NOT NULL, created_at TEXT NOT NULL)"
        )
        # Card payments leave the account for a shop, so they have no recipient.
        conn.execute(
            "CREATE TABLE IF NOT EXISTS card_payments ("
            " id INTEGER PRIMARY KEY AUTOINCREMENT, person INTEGER NOT NULL,"
            " amount INTEGER NOT NULL, note TEXT NOT NULL, created_at TEXT NOT NULL)"
        )
        # Income (e.g. salary) enters the account from outside the app, so it has no sender.
        conn.execute(
            "CREATE TABLE IF NOT EXISTS income ("
            " id INTEGER PRIMARY KEY AUTOINCREMENT, person INTEGER NOT NULL,"
            " amount INTEGER NOT NULL, note TEXT NOT NULL, created_at TEXT NOT NULL)"
        )
        # A request asks `payer` to send `amount` to `requester`. Requests created together
        # by Group Settle share a request_groups row.
        conn.execute(
            "CREATE TABLE IF NOT EXISTS request_groups ("
            " id INTEGER PRIMARY KEY AUTOINCREMENT,"
            " requester INTEGER NOT NULL, title TEXT NOT NULL, created_at TEXT NOT NULL)"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS requests ("
            " id INTEGER PRIMARY KEY AUTOINCREMENT,"
            " group_id INTEGER REFERENCES request_groups(id),"
            " requester INTEGER NOT NULL, payer INTEGER NOT NULL,"
            " amount INTEGER NOT NULL, note TEXT NOT NULL,"
            " status TEXT NOT NULL DEFAULT 'open',"  # open | paid | declined | cancelled
            " payment_id INTEGER REFERENCES payments(id),"
            " created_at TEXT NOT NULL)"
        )
        # Group Settle: a group of people sharing expenses until the creator approves it.
        conn.execute(
            "CREATE TABLE IF NOT EXISTS settle_groups ("
            " id INTEGER PRIMARY KEY AUTOINCREMENT,"
            " name TEXT NOT NULL, creator INTEGER NOT NULL,"
            " status TEXT NOT NULL DEFAULT 'open',"  # open | approved
            " created_at TEXT NOT NULL, approved_at TEXT)"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS settle_members ("
            " group_id INTEGER NOT NULL REFERENCES settle_groups(id), person INTEGER NOT NULL,"
            " PRIMARY KEY (group_id, person))"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS expenses ("
            " id INTEGER PRIMARY KEY AUTOINCREMENT,"
            " group_id INTEGER NOT NULL REFERENCES settle_groups(id),"
            " payer INTEGER NOT NULL, amount INTEGER NOT NULL,"
            " description TEXT NOT NULL, created_at TEXT NOT NULL)"
        )
        columns = [c["name"] for c in conn.execute("PRAGMA table_info(request_groups)")]
        if "settle_group_id" not in columns:
            # Requests created by approving a settle group point back to it.
            conn.execute("ALTER TABLE request_groups ADD COLUMN settle_group_id INTEGER")
        columns = [c["name"] for c in conn.execute("PRAGMA table_info(expenses)")]
        if "source_kind" not in columns:
            # An expense picked from history points at the payment it came from ("card" | "transfer").
            conn.execute("ALTER TABLE expenses ADD COLUMN source_kind TEXT")
            conn.execute("ALTER TABLE expenses ADD COLUMN source_id INTEGER")
        conn.execute(
            "CREATE TABLE IF NOT EXISTS recordings ("
            " person INTEGER PRIMARY KEY, started_at TEXT NOT NULL)"
        )
        for pid, name in PEOPLE.items():
            conn.execute(
                "INSERT INTO accounts (id, name, balance) VALUES (?, ?, ?)"
                " ON CONFLICT(id) DO UPDATE SET name = excluded.name",
                (pid, name, START_BALANCE),
            )


def reset_db(path):
    init_db(path)
    with _connect(path) as conn:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("DELETE FROM requests")
        conn.execute("DELETE FROM request_groups")
        conn.execute("DELETE FROM expenses")
        conn.execute("DELETE FROM settle_members")
        conn.execute("DELETE FROM settle_groups")
        conn.execute("DELETE FROM payments")
        conn.execute("DELETE FROM card_payments")
        conn.execute("DELETE FROM income")
        conn.execute("DELETE FROM recordings")
        conn.execute("UPDATE accounts SET balance = ?", (START_BALANCE,))
        conn.execute("COMMIT")


def get_balance(path, person_id):
    with _connect(path) as conn:
        row = conn.execute("SELECT balance FROM accounts WHERE id = ?", (person_id,)).fetchone()
    if row is None:
        raise PaymentError(f"Neznámá osoba {person_id}")
    return row["balance"]


def _now():
    return datetime.now().isoformat(timespec="seconds")


def _check_amount(amount):
    if type(amount) is not int or amount <= 0:
        raise PaymentError("Částka musí být celé číslo korun větší než nula")


def _check_pair(me, other, unknown="Neznámý příjemce", self_msg="Nemůžeš platit sám sobě"):
    if me not in PEOPLE or other not in PEOPLE:
        raise PaymentError(unknown)
    if me == other:
        raise PaymentError(self_msg)


@contextmanager
def _transaction(path):
    with _connect(path) as conn:
        conn.execute("BEGIN IMMEDIATE")
        try:
            yield conn
            conn.execute("COMMIT")
        except BaseException:
            conn.execute("ROLLBACK")
            raise


def _debit(conn, person, amount):
    """Take money from an account inside an open transaction, if it has enough."""
    balance = conn.execute("SELECT balance FROM accounts WHERE id = ?", (person,)).fetchone()["balance"]
    if balance < amount:
        raise PaymentError("Nedostatek prostředků")
    conn.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (amount, person))


def _transfer(conn, sender, recipient, amount, note):
    """Move money inside an open transaction and record the payment."""
    _debit(conn, sender, amount)
    conn.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (amount, recipient))
    created_at = _now()
    cur = conn.execute(
        "INSERT INTO payments (sender, recipient, amount, note, created_at) VALUES (?, ?, ?, ?, ?)",
        (sender, recipient, amount, note, created_at),
    )
    return {
        "id": cur.lastrowid,
        "sender": sender,
        "recipient": recipient,
        "amount": amount,
        "note": note,
        "created_at": created_at,
    }


def send_payment(path, sender, recipient, amount, note=""):
    _check_amount(amount)
    _check_pair(sender, recipient)
    with _transaction(path) as conn:
        return _transfer(conn, sender, recipient, amount, (note or "").strip())


CARD_NOTE_MAX = 60


def card_payment(path, person, amount, note=""):
    """Pay a shop by card: the money leaves `person`'s account and goes nowhere in the app."""
    _check_amount(amount)
    if person not in PEOPLE:
        raise PaymentError("Neznámá osoba")
    note = (note or "").strip()
    if len(note) > CARD_NOTE_MAX:
        raise PaymentError(f"Poznámka může mít nejvýše {CARD_NOTE_MAX} znaků")
    with _transaction(path) as conn:
        _debit(conn, person, amount)
        created_at = _now()
        cur = conn.execute(
            "INSERT INTO card_payments (person, amount, note, created_at) VALUES (?, ?, ?, ?)",
            (person, amount, note, created_at),
        )
    return {"id": cur.lastrowid, "person": person, "amount": amount, "note": note, "created_at": created_at}


def _recording(conn, person):
    row = conn.execute("SELECT started_at FROM recordings WHERE person = ?", (person,)).fetchone()
    if row is None:
        return None
    payments = [
        dict(r) for r in conn.execute(
            "SELECT * FROM card_payments WHERE person = ? AND created_at >= ? ORDER BY created_at, id",
            (person, row["started_at"]),
        )
    ]
    return {"started_at": row["started_at"], "payments": payments, "total": sum(p["amount"] for p in payments)}


def start_recording(path, person):
    """Start collecting `person`'s card payments (for a Group Payment)."""
    if person not in PEOPLE:
        raise PaymentError("Neznámá osoba")
    with _transaction(path) as conn:
        if conn.execute("SELECT 1 FROM recordings WHERE person = ?", (person,)).fetchone():
            raise PaymentError("Skupinová platba už běží")
        started_at = _now()
        conn.execute("INSERT INTO recordings (person, started_at) VALUES (?, ?)", (person, started_at))
    return {"started_at": started_at}


def recording(path, person):
    """The running recording with the card payments made since it started, or None."""
    with _connect(path) as conn:
        return _recording(conn, person)


def stop_recording(path, person):
    """End the recording and return what it collected."""
    with _transaction(path) as conn:
        result = _recording(conn, person)
        if result is None:
            raise PaymentError("Žádná skupinová platba neběží")
        conn.execute("DELETE FROM recordings WHERE person = ?", (person,))
    return result


def add_income(path, person, amount, note=""):
    """Credit `person` with money from outside the app, e.g. a salary."""
    _check_amount(amount)
    if person not in PEOPLE:
        raise PaymentError("Neznámá osoba")
    note = (note or "").strip()
    with _transaction(path) as conn:
        conn.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (amount, person))
        created_at = _now()
        cur = conn.execute(
            "INSERT INTO income (person, amount, note, created_at) VALUES (?, ?, ?, ?)",
            (person, amount, note, created_at),
        )
    return {"id": cur.lastrowid, "person": person, "amount": amount, "note": note, "created_at": created_at}


def history(path, person_id):
    """Transfers, card payments and income of one person, newest first."""
    with _connect(path) as conn:
        transfers = conn.execute(
            "SELECT * FROM payments WHERE sender = ? OR recipient = ?", (person_id, person_id)
        ).fetchall()
        cards = conn.execute("SELECT * FROM card_payments WHERE person = ?", (person_id,)).fetchall()
        income = conn.execute("SELECT * FROM income WHERE person = ?", (person_id,)).fetchall()
    items = [{"kind": "transfer", **dict(r)} for r in transfers]
    items += [{"kind": "card", **dict(r)} for r in cards]
    items += [{"kind": "income", **dict(r)} for r in income]
    items.sort(key=lambda i: (i["created_at"], i["id"]), reverse=True)
    return items


def day_change(path, person_id, day=None):
    """How much `person_id`'s balance moved on `day` ("YYYY-MM-DD", default today): in minus out."""
    day = day or _now()[:10]
    change = 0
    for item in history(path, person_id):
        if item["created_at"][:10] != day:
            continue
        incoming = item["kind"] == "income" or (item["kind"] == "transfer" and item["recipient"] == person_id)
        change += item["amount"] if incoming else -item["amount"]
    return change


# ---- payment requests ----


def _insert_request(conn, requester, payer, amount, note, group_id=None):
    created_at = _now()
    cur = conn.execute(
        "INSERT INTO requests (group_id, requester, payer, amount, note, created_at)"
        " VALUES (?, ?, ?, ?, ?, ?)",
        (group_id, requester, payer, amount, note, created_at),
    )
    return {
        "id": cur.lastrowid,
        "group_id": group_id,
        "requester": requester,
        "payer": payer,
        "amount": amount,
        "note": note,
        "status": "open",
        "created_at": created_at,
    }


def create_request(path, requester, payer, amount, note=""):
    """Ask `payer` to send `amount` CZK to `requester`."""
    _check_amount(amount)
    _check_pair(requester, payer, "Neznámý kontakt", "Nemůžeš žádat peníze sám od sebe")
    with _transaction(path) as conn:
        return _insert_request(conn, requester, payer, amount, (note or "").strip())


def create_group_request(path, requester, title, shares, note=""):
    """One request per payer in `shares` ({payer_id: amount}), grouped under `title`."""
    if not shares:
        raise PaymentError("Vyber alespoň jednu osobu")
    for payer, amount in shares.items():
        _check_amount(amount)
        _check_pair(requester, payer, "Neznámý kontakt", "Nemůžeš žádat peníze sám od sebe")
    title = (title or "").strip() or "Skupinová platba"
    note = (note or "").strip()
    with _transaction(path) as conn:
        created_at = _now()
        group_id = conn.execute(
            "INSERT INTO request_groups (requester, title, created_at) VALUES (?, ?, ?)",
            (requester, title, created_at),
        ).lastrowid
        requests = [_insert_request(conn, requester, p, a, note, group_id) for p, a in shares.items()]
    return {
        "id": group_id,
        "requester": requester,
        "title": title,
        "total": sum(shares.values()),
        "created_at": created_at,
        "requests": requests,
    }


def _group_info(conn, group_id):
    g = conn.execute("SELECT * FROM request_groups WHERE id = ?", (group_id,)).fetchone()
    members = conn.execute(
        "SELECT payer, requester, amount, status FROM requests WHERE group_id = ? ORDER BY id", (group_id,)
    ).fetchall()
    return {
        "id": g["id"],
        "title": g["title"],
        "requester": g["requester"],
        "settle_group_id": g["settle_group_id"],
        "total": sum(m["amount"] for m in members),
        "members": [dict(m) for m in members],
    }


def open_requests_for(path, payer):
    """Open requests `payer` still has to pay, newest first; group ones carry group info."""
    with _connect(path) as conn:
        rows = conn.execute(
            "SELECT * FROM requests WHERE payer = ? AND status = 'open' ORDER BY id DESC", (payer,)
        ).fetchall()
        result = []
        for r in rows:
            item = dict(r)
            item["group"] = _group_info(conn, r["group_id"]) if r["group_id"] else None
            result.append(item)
    return result


def requests_by(path, requester):
    """Every request `requester` has made (any status), newest first; group ones carry group info."""
    with _connect(path) as conn:
        rows = conn.execute(
            "SELECT * FROM requests WHERE requester = ? ORDER BY id DESC", (requester,)
        ).fetchall()
        result = []
        for r in rows:
            item = dict(r)
            item["group"] = _group_info(conn, r["group_id"]) if r["group_id"] else None
            result.append(item)
    return result


def _open_request(conn, request_id, payer):
    r = conn.execute("SELECT * FROM requests WHERE id = ?", (request_id,)).fetchone()
    if r is None or r["payer"] != payer:
        raise PaymentError("Žádost nebyla nalezena")
    if r["status"] != "open":
        raise PaymentError("Tato žádost už není otevřená")
    return r


def pay_request(path, request_id, payer):
    """Pay an open request. Returns the payment; the request is marked paid."""
    with _transaction(path) as conn:
        r = _open_request(conn, request_id, payer)
        payment = _transfer(conn, payer, r["requester"], r["amount"], r["note"])
        conn.execute(
            "UPDATE requests SET status = 'paid', payment_id = ? WHERE id = ?", (payment["id"], request_id)
        )
    return payment


def get_request(path, request_id):
    with _connect(path) as conn:
        r = conn.execute("SELECT * FROM requests WHERE id = ?", (request_id,)).fetchone()
    return dict(r) if r else None


def decline_request(path, request_id, payer):
    with _transaction(path) as conn:
        r = dict(_open_request(conn, request_id, payer))
        conn.execute("UPDATE requests SET status = 'declined' WHERE id = ?", (request_id,))
    r["status"] = "declined"
    return r


# ---- Group Settle ----

GROUP_NAME_MAX = 40
EXPENSE_DESC_MAX = 60


def _text(value, max_len, what):
    if not isinstance(value, str) or not value.strip():
        raise PaymentError(f"Vyplň pole „{what}“")
    value = value.strip()
    if len(value) > max_len:
        raise PaymentError(f"Pole „{what}“ může mít nejvýše {max_len} znaků")
    return value


def _group_row(conn, group_id, person):
    g = conn.execute("SELECT * FROM settle_groups WHERE id = ?", (group_id,)).fetchone()
    member = g and conn.execute(
        "SELECT 1 FROM settle_members WHERE group_id = ? AND person = ?", (group_id, person)
    ).fetchone()
    if not member:
        raise PaymentError("Skupina nebyla nalezena")
    return g


def _require_open(g):
    if g["status"] != "open":
        raise PaymentError("Tato skupina je už schválená")


def _group_dict(conn, g):
    members = [r["person"] for r in conn.execute(
        "SELECT person FROM settle_members WHERE group_id = ? ORDER BY person", (g["id"],))]
    expenses = [dict(r) for r in conn.execute(
        "SELECT * FROM expenses WHERE group_id = ? ORDER BY id DESC", (g["id"],))]
    requests_sent = conn.execute(
        "SELECT COUNT(*) FROM requests r JOIN request_groups rg ON rg.id = r.group_id"
        " WHERE rg.settle_group_id = ?",
        (g["id"],),
    ).fetchone()[0]
    return {
        **dict(g),
        "members": members,
        "expenses": expenses,
        "total": sum(e["amount"] for e in expenses),
        "requests_sent": requests_sent,
    }


def create_group(path, creator, name, members, expense=None, sources=None):
    """A new open group of `creator` plus `members` (ids of other people).

    `expense` ({"amount", "description"}) is a first expense paid by `creator`.
    `sources` ([{"kind", "id"}, ...]) are `creator`'s own payments added as expenses."""
    name = _text(name, GROUP_NAME_MAX, "Název skupiny")
    if not isinstance(members, list) or not members:
        raise PaymentError("Přidej alespoň jednu osobu")
    for m in members:
        if type(m) is not int or m not in PEOPLE or m == creator:
            raise PaymentError("Přidat můžeš jen ostatní lidi")
    if creator not in PEOPLE:
        raise PaymentError("Neznámá osoba")
    if expense is not None:
        if not isinstance(expense, dict):
            raise PaymentError("Výdaj musí mít částku a popis")
        _check_amount(expense.get("amount"))
        description = _text(expense.get("description"), EXPENSE_DESC_MAX, "Za co to bylo")
    sources = _check_sources(sources)
    with _transaction(path) as conn:
        group_id = conn.execute(
            "INSERT INTO settle_groups (name, creator, created_at) VALUES (?, ?, ?)",
            (name, creator, _now()),
        ).lastrowid
        for person in {creator, *members}:
            conn.execute("INSERT INTO settle_members (group_id, person) VALUES (?, ?)", (group_id, person))
        if expense is not None:
            conn.execute(
                "INSERT INTO expenses (group_id, payer, amount, description, created_at) VALUES (?, ?, ?, ?, ?)",
                (group_id, creator, expense["amount"], description, _now()),
            )
        for source in sources:
            _expense_from_payment(conn, group_id, creator, source["kind"], source["id"])
        g = conn.execute("SELECT * FROM settle_groups WHERE id = ?", (group_id,)).fetchone()
        return _group_dict(conn, g)


def _insert_expense(conn, group_id, payer, amount, description, source_kind=None, source_id=None):
    created_at = _now()
    expense_id = conn.execute(
        "INSERT INTO expenses (group_id, payer, amount, description, created_at, source_kind, source_id)"
        " VALUES (?, ?, ?, ?, ?, ?, ?)",
        (group_id, payer, amount, description, created_at, source_kind, source_id),
    ).lastrowid
    return {
        "id": expense_id,
        "group_id": group_id,
        "payer": payer,
        "amount": amount,
        "description": description,
        "created_at": created_at,
        "source_kind": source_kind,
        "source_id": source_id,
    }


def add_expense(path, group_id, payer, amount, description):
    """Record that `payer` paid `amount` for the group. No money moves."""
    _check_amount(amount)
    description = _text(description, EXPENSE_DESC_MAX, "Za co to bylo")
    with _transaction(path) as conn:
        _require_open(_group_row(conn, group_id, payer))
        return _insert_expense(conn, group_id, payer, amount, description)


def _check_sources(sources):
    if sources is None:
        return []
    if not isinstance(sources, list) or not all(
        isinstance(x, dict) and type(x.get("id")) is int for x in sources
    ):
        raise PaymentError("Vyber platbu ze své historie")
    return sources


def _expense_from_payment(conn, group_id, payer, kind, payment_id):
    """Insert `payer`'s own payment as an expense of the group; the caller owns the transaction."""
    if kind == "card":
        row = conn.execute(
            "SELECT amount, note FROM card_payments WHERE id = ? AND person = ?", (payment_id, payer)
        ).fetchone()
        default = "Platba kartou"
    elif kind == "transfer":
        row = conn.execute(
            "SELECT amount, note, recipient FROM payments WHERE id = ? AND sender = ?", (payment_id, payer)
        ).fetchone()
        default = row and f"Platba pro {PEOPLE[row['recipient']]}"
    else:
        row = None
    if row is None:
        raise PaymentError("Platba nebyla nalezena")
    if conn.execute(
        "SELECT 1 FROM expenses WHERE group_id = ? AND source_kind = ? AND source_id = ?",
        (group_id, kind, payment_id),
    ).fetchone():
        raise PaymentError("Tato platba už ve skupině je")
    description = (row["note"] or default)[:EXPENSE_DESC_MAX]
    return _insert_expense(conn, group_id, payer, row["amount"], description, kind, payment_id)


def add_expense_from_payment(path, group_id, payer, kind, payment_id):
    """Add one of `payer`'s own outgoing payments (a card payment or a transfer they sent)."""
    with _transaction(path) as conn:
        _require_open(_group_row(conn, group_id, payer))
        return _expense_from_payment(conn, group_id, payer, kind, payment_id)


def add_expenses_from_payments(path, group_id, payer, sources):
    """Add several of `payer`'s payments at once. Ones already in the group are skipped, any other bad one aborts all."""
    sources = _check_sources(sources)
    added, skipped = [], 0
    with _transaction(path) as conn:
        _require_open(_group_row(conn, group_id, payer))
        for source in sources:
            if conn.execute(
                "SELECT 1 FROM expenses WHERE group_id = ? AND source_kind = ? AND source_id = ?",
                (group_id, source.get("kind"), source["id"]),
            ).fetchone():
                skipped += 1
            else:
                added.append(_expense_from_payment(conn, group_id, payer, source.get("kind"), source["id"]))
    return {"added": added, "skipped": skipped}


def delete_expense(path, group_id, expense_id, person):
    with _transaction(path) as conn:
        _require_open(_group_row(conn, group_id, person))
        e = conn.execute(
            "SELECT payer FROM expenses WHERE id = ? AND group_id = ?", (expense_id, group_id)
        ).fetchone()
        if e is None:
            raise PaymentError("Výdaj nebyl nalezen")
        if e["payer"] != person:
            raise PaymentError("Smazat můžeš jen vlastní výdaje")
        conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))


def approve_group(path, group_id, person, split=None):
    """Creator only: lock the group and turn the split into payment requests."""
    split = split or split_slot.settle
    with _transaction(path) as conn:
        g = _group_row(conn, group_id, person)
        if g["creator"] != person:
            raise PaymentError("Skupinu může schválit jen její zakladatel")
        _require_open(g)
        info = _group_dict(conn, g)
        transfers = split(list(info["members"]), list(reversed(info["expenses"])))
        requests = []
        if transfers:
            request_group = conn.execute(
                "INSERT INTO request_groups (requester, title, created_at, settle_group_id) VALUES (?, ?, ?, ?)",
                (g["creator"], g["name"], _now(), group_id),
            ).lastrowid
            for payer, payee, amount in transfers:
                if payer not in info["members"] or payee not in info["members"] or payer == payee:
                    raise PaymentError("Vyrovnání vrátilo platbu mimo skupinu")
                _check_amount(amount)
                requests.append(_insert_request(conn, payee, payer, amount, "", request_group))
        conn.execute(
            "UPDATE settle_groups SET status = 'approved', approved_at = ? WHERE id = ?", (_now(), group_id)
        )
        info = _group_dict(conn, conn.execute("SELECT * FROM settle_groups WHERE id = ?", (group_id,)).fetchone())
    info["requests"] = requests
    return info


def delete_group(path, group_id, person):
    """Creator only: remove the group for everyone and cancel its settlement requests still open.

    Paid requests stay paid: that money has really moved.
    """
    with _transaction(path) as conn:
        g = _group_row(conn, group_id, person)
        if g["creator"] != person:
            raise PaymentError("Skupinu může smazat jen její zakladatel")
        info = _group_dict(conn, g)
        cancelled = [dict(r) for r in conn.execute(
            "SELECT r.* FROM requests r JOIN request_groups rg ON rg.id = r.group_id"
            " WHERE rg.settle_group_id = ? AND r.status = 'open' ORDER BY r.id",
            (group_id,),
        )]
        conn.execute(
            "UPDATE requests SET status = 'cancelled' WHERE status = 'open' AND group_id IN"
            " (SELECT id FROM request_groups WHERE settle_group_id = ?)",
            (group_id,),
        )
        conn.execute("DELETE FROM expenses WHERE group_id = ?", (group_id,))
        conn.execute("DELETE FROM settle_members WHERE group_id = ?", (group_id,))
        conn.execute("DELETE FROM settle_groups WHERE id = ?", (group_id,))
    for r in cancelled:
        r["status"] = "cancelled"
    return {"id": group_id, "name": info["name"], "members": info["members"], "cancelled": cancelled}


def groups_for(path, person):
    """Every group `person` is in, newest first."""
    with _connect(path) as conn:
        rows = conn.execute(
            "SELECT g.* FROM settle_groups g JOIN settle_members m ON m.group_id = g.id"
            " WHERE m.person = ? ORDER BY g.id DESC",
            (person,),
        ).fetchall()
        return [_group_dict(conn, g) for g in rows]
