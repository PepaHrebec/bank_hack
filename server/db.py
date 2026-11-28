"""SQLite storage for the payments and payment requests of the four mockup people."""

import re
import sqlite3
from contextlib import contextmanager
from datetime import datetime

from server import settle as split_slot

PEOPLE = {1: "Štěpán Pressl", 2: "Jirka Měřínský", 3: "Pepa Hřebec", 4: "Petr Šafář"}
GEOFF_BANK = "0800"  # bank code of accounts held at Geoff
# Each person's Geoff account: person N has NNNNNNNNNN/0800 (repeated digits pass the mod-11 check).
ACCOUNTS = {pid: f"{str(pid) * 10}/{GEOFF_BANK}" for pid in PEOPLE}
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
        # Account payments leave the account for a Czech bank account outside the app.
        conn.execute(
            "CREATE TABLE IF NOT EXISTS account_payments ("
            " id INTEGER PRIMARY KEY AUTOINCREMENT, person INTEGER NOT NULL, account TEXT NOT NULL,"
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
        columns = [c["name"] for c in conn.execute("PRAGMA table_info(settle_members)")]
        if "status" not in columns:
            # 'invited' until the person accepts; only 'accepted' people are in the group.
            conn.execute("ALTER TABLE settle_members ADD COLUMN status TEXT NOT NULL DEFAULT 'accepted'")
        columns = [c["name"] for c in conn.execute("PRAGMA table_info(expenses)")]
        if "source_kind" not in columns:
            # An expense picked from history points at the payment it came from ("card" | "transfer").
            conn.execute("ALTER TABLE expenses ADD COLUMN source_kind TEXT")
            conn.execute("ALTER TABLE expenses ADD COLUMN source_id INTEGER")
        conn.execute(
            "CREATE TABLE IF NOT EXISTS recordings ("
            " person INTEGER PRIMARY KEY, started_at TEXT NOT NULL)"
        )
        columns = [c["name"] for c in conn.execute("PRAGMA table_info(recordings)")]
        if "session_starter" not in columns:
            # A shared session: every participant's row points at the person who started it.
            conn.execute("ALTER TABLE recordings ADD COLUMN session_starter INTEGER")
            conn.execute("ALTER TABLE recordings ADD COLUMN ended_at TEXT")
        conn.execute("UPDATE recordings SET session_starter = person WHERE session_starter IS NULL")
        conn.execute(
            "CREATE TABLE IF NOT EXISTS session_invites ("
            " starter INTEGER NOT NULL, person INTEGER NOT NULL, PRIMARY KEY (starter, person))"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS messages ("
            " id INTEGER PRIMARY KEY AUTOINCREMENT,"
            " sender INTEGER NOT NULL, recipient INTEGER NOT NULL,"
            " text TEXT NOT NULL, created_at TEXT NOT NULL)"
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
        conn.execute("DELETE FROM account_payments")
        conn.execute("DELETE FROM income")
        conn.execute("DELETE FROM recordings")
        conn.execute("DELETE FROM session_invites")
        conn.execute("DELETE FROM messages")
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


_ACCOUNT_RE = re.compile(r"(?:([0-9]{1,6})-)?([0-9]{2,10})/([0-9]{4})")
_ACCOUNT_WEIGHTS = (1, 2, 4, 8, 5, 10, 9, 7, 3, 6)  # from the rightmost digit


def _mod11_ok(digits):
    return sum(int(d) * w for d, w in zip(reversed(digits), _ACCOUNT_WEIGHTS)) % 11 == 0


def parse_account(text):
    """Validate a Czech account number `[prefix-]number/bank` and return its normalised form."""
    match = _ACCOUNT_RE.fullmatch(re.sub(r"\s+", "", text)) if isinstance(text, str) else None
    if not match:
        raise PaymentError("Neplatné číslo účtu")
    prefix, number, bank = match.groups()
    prefix = prefix or ""
    if int(number) == 0 or not _mod11_ok(prefix) or not _mod11_ok(number):
        raise PaymentError("Neplatné číslo účtu")
    prefix, number = prefix.lstrip("0"), number.lstrip("0")
    return f"{prefix + '-' if prefix else ''}{number}/{bank}"


def person_by_account(text):
    """The person holding Czech account `text` at Geoff, or None (invalid numbers raise PaymentError)."""
    account = parse_account(text)
    return next((pid for pid, acc in ACCOUNTS.items() if acc == account), None)


def account_payment(path, person, account, amount, note=""):
    """Pay a Czech bank account. An account of another Geoff person is a normal transfer
    (returned with "kind": "transfer"); otherwise the money leaves the app."""
    _check_amount(amount)
    if person not in PEOPLE:
        raise PaymentError("Neznámá osoba")
    account = parse_account(account)
    recipient = person_by_account(account)
    if recipient == person:
        raise PaymentError("Nelze platit na vlastní účet")
    if recipient is not None:
        return {"kind": "transfer", **send_payment(path, person, recipient, amount, note)}
    note = (note or "").strip()
    with _transaction(path) as conn:
        _debit(conn, person, amount)
        created_at = _now()
        cur = conn.execute(
            "INSERT INTO account_payments (person, account, amount, note, created_at) VALUES (?, ?, ?, ?, ?)",
            (person, account, amount, note, created_at),
        )
    return {"id": cur.lastrowid, "person": person, "account": account, "amount": amount, "note": note,
            "created_at": created_at}


def _own_payments(conn, person, since, until=None):
    sql = "SELECT * FROM card_payments WHERE person = ? AND created_at >= ?"
    args = [person, since]
    if until is not None:
        sql += " AND created_at <= ?"
        args.append(until)
    return [dict(r) for r in conn.execute(sql + " ORDER BY created_at, id", args)]


def _participants(conn, starter, ended):
    """Ids of the session's accepted people (the starter first), running or ended."""
    rows = conn.execute(
        "SELECT person FROM recordings WHERE session_starter = ? AND person != ?"
        + (" AND ended_at IS NOT NULL" if ended else " AND ended_at IS NULL") + " ORDER BY person",
        (starter, starter),
    )
    return [starter] + [r["person"] for r in rows]


def _session_invited(conn, starter):
    return [r["person"] for r in conn.execute(
        "SELECT person FROM session_invites WHERE starter = ? ORDER BY person", (starter,)
    )]


def _recording(conn, person):
    row = conn.execute(
        "SELECT started_at, session_starter FROM recordings WHERE person = ? AND ended_at IS NULL", (person,)
    ).fetchone()
    if row is None:
        return None
    payments = _own_payments(conn, person, row["started_at"])
    starter = row["session_starter"]
    return {
        "started_at": row["started_at"],
        "payments": payments,
        "total": sum(p["amount"] for p in payments),
        "starter": starter,
        "participants": _participants(conn, starter, ended=False),
        "invited": _session_invited(conn, starter),
    }


def start_recording(path, person, invite=()):
    """Start collecting `person`'s card payments (for a Group Payment), inviting friends to join."""
    if person not in PEOPLE:
        raise PaymentError("Neznámá osoba")
    invited = sorted({i for i in invite if type(i) is int and i in PEOPLE and i != person})
    with _transaction(path) as conn:
        if conn.execute(
            "SELECT 1 FROM recordings WHERE person = ? AND ended_at IS NULL", (person,)
        ).fetchone():
            raise PaymentError("Skupinová platba už běží")
        _clear_ended_row(conn, person)
        started_at = _now()
        conn.execute(
            "INSERT INTO recordings (person, started_at, session_starter) VALUES (?, ?, ?)",
            (person, started_at, person),
        )
        for other in invited:
            conn.execute("INSERT INTO session_invites (starter, person) VALUES (?, ?)", (person, other))
    return {"started_at": started_at, "invited": invited}


def _clear_ended_row(conn, person):
    """`person` has no running recording; free their row if it's their own finished session."""
    row = conn.execute("SELECT session_starter FROM recordings WHERE person = ?", (person,)).fetchone()
    if row is None:
        return
    if row["session_starter"] != person:
        # Not running (callers checked), so it is someone else's ended session awaiting its group.
        raise PaymentError(f"Čeká se, až {PEOPLE[row['session_starter']].split()[0]} dokončí skupinovou platbu")
    _delete_session(conn, person)


def _delete_session(conn, starter):
    conn.execute("DELETE FROM recordings WHERE session_starter = ?", (starter,))
    conn.execute("DELETE FROM session_invites WHERE starter = ?", (starter,))


def accept_session_invite(path, person, starter):
    with _transaction(path) as conn:
        invite = conn.execute(
            "SELECT 1 FROM session_invites WHERE starter = ? AND person = ?", (starter, person)
        ).fetchone()
        running = conn.execute(
            "SELECT 1 FROM recordings WHERE person = ? AND session_starter = ? AND ended_at IS NULL",
            (starter, starter),
        ).fetchone()
        if invite is None or running is None:
            raise PaymentError("Skupinová platba už skončila")
        if conn.execute("SELECT 1 FROM recordings WHERE person = ? AND ended_at IS NULL", (person,)).fetchone():
            raise PaymentError("Už jsi v jiné skupinové platbě")
        _clear_ended_row(conn, person)
        conn.execute(
            "INSERT INTO recordings (person, started_at, session_starter) VALUES (?, ?, ?)",
            (person, _now(), starter),
        )
        conn.execute("DELETE FROM session_invites WHERE starter = ? AND person = ?", (starter, person))
        return _recording(conn, person)


def decline_session_invite(path, person, starter):
    with _transaction(path) as conn:
        if conn.execute(
            "DELETE FROM session_invites WHERE starter = ? AND person = ?", (starter, person)
        ).rowcount == 0:
            raise PaymentError("Pozvánka nebyla nalezena")
    return {"starter": starter}


def session_invites_for(path, person):
    with _connect(path) as conn:
        return [
            {"starter": r["starter"], "started_at": r["started_at"]}
            for r in conn.execute(
                "SELECT i.starter, r.started_at FROM session_invites i"
                " JOIN recordings r ON r.person = i.starter AND r.ended_at IS NULL"
                " WHERE i.person = ? ORDER BY r.started_at, i.starter",
                (person,),
            )
        ]


def recording(path, person):
    """The running recording with the card payments made since it started, or None."""
    with _connect(path) as conn:
        return _recording(conn, person)


def stop_recording(path, person):
    """End the recording (only its starter can) and return what it collected."""
    with _transaction(path) as conn:
        result = _recording(conn, person)
        if result is None:
            raise PaymentError("Žádná skupinová platba neběží")
        if result["starter"] != person:
            raise PaymentError("Skupinovou platbu může ukončit jen ten, kdo ji spustil")
        conn.execute("DELETE FROM session_invites WHERE starter = ?", (person,))
        if len(result["participants"]) == 1:
            conn.execute("DELETE FROM recordings WHERE person = ?", (person,))
            return {k: result[k] for k in ("started_at", "payments", "total", "participants")}
        ended_at = _now()
        payments = []
        for p in result["participants"]:
            since = conn.execute("SELECT started_at FROM recordings WHERE person = ?", (p,)).fetchone()["started_at"]
            payments += _own_payments(conn, p, since, ended_at)
        payments.sort(key=lambda x: (x["created_at"], x["id"]))
        conn.execute(
            "UPDATE recordings SET ended_at = ? WHERE session_starter = ? AND ended_at IS NULL", (ended_at, person)
        )
    return {
        "started_at": result["started_at"],
        "payments": payments,
        "total": sum(p["amount"] for p in payments),
        "participants": result["participants"],
        "shared": True,
    }


def _ended_session_payments(conn, starter):
    participants = _participants(conn, starter, ended=True)
    if len(participants) < 2 or not conn.execute(
        "SELECT 1 FROM recordings WHERE person = ? AND ended_at IS NOT NULL", (starter,)
    ).fetchone():
        raise PaymentError("Žádná ukončená skupinová platba")
    payments = []
    for p in participants:
        r = conn.execute("SELECT started_at, ended_at FROM recordings WHERE person = ?", (p,)).fetchone()
        payments += _own_payments(conn, p, r["started_at"], r["ended_at"])
    payments.sort(key=lambda x: (x["created_at"], x["id"]))
    return participants, payments


def create_group_from_session(path, starter, name):
    """Turn the starter's finished shared session into a group; everyone who joined is already in."""
    name = _text(name, GROUP_NAME_MAX, "Název skupiny")
    with _transaction(path) as conn:
        participants, payments = _ended_session_payments(conn, starter)
        group = _insert_group(conn, starter, name, participants[1:], True, None, [])
        for p in payments:
            _expense_from_payment(conn, group["id"], p["person"], "card", p["id"])
        _delete_session(conn, starter)
        g = conn.execute("SELECT * FROM settle_groups WHERE id = ?", (group["id"],)).fetchone()
        return _group_dict(conn, g)


def discard_session(path, starter):
    """Drop the starter's finished session without making a group."""
    with _transaction(path) as conn:
        if conn.execute(
            "SELECT 1 FROM recordings WHERE person = ? AND ended_at IS NOT NULL", (starter,)
        ).fetchone():
            _delete_session(conn, starter)


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
        accounts = conn.execute("SELECT * FROM account_payments WHERE person = ?", (person_id,)).fetchall()
        income = conn.execute("SELECT * FROM income WHERE person = ?", (person_id,)).fetchall()
    items = [{"kind": "transfer", **dict(r)} for r in transfers]
    items += [{"kind": "card", **dict(r)} for r in cards]
    items += [{"kind": "account", **dict(r)} for r in accounts]
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
        "SELECT 1 FROM settle_members WHERE group_id = ? AND person = ? AND status = 'accepted'",
        (group_id, person),
    ).fetchone()
    if not member:
        raise PaymentError("Skupina nebyla nalezena")
    return g


def _require_open(g):
    if g["status"] != "open":
        raise PaymentError("Tato skupina je už schválená")


def _group_dict(conn, g):
    members, invited = ([r["person"] for r in conn.execute(
        "SELECT person FROM settle_members WHERE group_id = ? AND status = ? ORDER BY person",
        (g["id"], status))] for status in ("accepted", "invited"))
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
        "invited": invited,
        "expenses": expenses,
        "total": sum(e["amount"] for e in expenses),
        "requests_sent": requests_sent,
    }


def create_group(path, creator, name, members, expense=None, sources=None, accepted=False):
    """A new open group of `creator` plus `members` (ids of other people).

    Members are only invited until they accept, unless `accepted` is set.

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
        expense = {**expense, "description": _text(expense.get("description"), EXPENSE_DESC_MAX, "Za co to bylo")}
    sources = _check_sources(sources)
    with _transaction(path) as conn:
        return _insert_group(conn, creator, name, members, accepted, expense, sources)


def _insert_group(conn, creator, name, members, accepted, expense, sources):
    """Insert a validated group; the caller owns the transaction."""
    group_id = conn.execute(
        "INSERT INTO settle_groups (name, creator, created_at) VALUES (?, ?, ?)",
        (name, creator, _now()),
    ).lastrowid
    for person in {creator, *members}:
        status = "accepted" if accepted or person == creator else "invited"
        conn.execute(
            "INSERT INTO settle_members (group_id, person, status) VALUES (?, ?, ?)",
            (group_id, person, status),
        )
    if expense is not None:
        conn.execute(
            "INSERT INTO expenses (group_id, payer, amount, description, created_at) VALUES (?, ?, ?, ?, ?)",
            (group_id, creator, expense["amount"], expense["description"], _now()),
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
        cancelled_invites = info["invited"]
        conn.execute("DELETE FROM settle_members WHERE group_id = ? AND status = 'invited'", (group_id,))
        conn.execute(
            "UPDATE settle_groups SET status = 'approved', approved_at = ? WHERE id = ?", (_now(), group_id)
        )
        info = _group_dict(conn, conn.execute("SELECT * FROM settle_groups WHERE id = ?", (group_id,)).fetchone())
    info["requests"] = requests
    info["cancelled_invites"] = cancelled_invites
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
    return {
        "id": group_id, "name": info["name"], "members": info["members"],
        "invited": info["invited"], "cancelled": cancelled,
    }


def groups_for(path, person):
    """Every group `person` is in (has accepted), newest first."""
    return _groups_with_status(path, person, "accepted")


def group_invites_for(path, person):
    """Open groups `person` has been invited to but not yet joined, newest first."""
    return _groups_with_status(path, person, "invited")


def _groups_with_status(path, person, status):
    with _connect(path) as conn:
        rows = conn.execute(
            "SELECT g.* FROM settle_groups g JOIN settle_members m ON m.group_id = g.id"
            " WHERE m.person = ? AND m.status = ? AND (? = 'accepted' OR g.status = 'open')"
            " ORDER BY g.id DESC",
            (person, status, status),
        ).fetchall()
        return [_group_dict(conn, g) for g in rows]


def _invite(conn, group_id, person):
    g = conn.execute("SELECT * FROM settle_groups WHERE id = ?", (group_id,)).fetchone()
    invited = g and g["status"] == "open" and conn.execute(
        "SELECT 1 FROM settle_members WHERE group_id = ? AND person = ? AND status = 'invited'",
        (group_id, person),
    ).fetchone()
    if not invited:
        raise PaymentError("Pozvánka nebyla nalezena")
    return g


def accept_group_invite(path, group_id, person):
    """`person` joins the group they were invited to."""
    with _transaction(path) as conn:
        g = _invite(conn, group_id, person)
        conn.execute(
            "UPDATE settle_members SET status = 'accepted' WHERE group_id = ? AND person = ?",
            (group_id, person),
        )
        return _group_dict(conn, g)


def decline_group_invite(path, group_id, person):
    """`person` turns the invitation down; it disappears."""
    with _transaction(path) as conn:
        g = _invite(conn, group_id, person)
        conn.execute("DELETE FROM settle_members WHERE group_id = ? AND person = ?", (group_id, person))
        return {"id": group_id, "name": g["name"], "creator": g["creator"]}


# ---- WhatsApp mock-up: one-to-one messages ----

MESSAGE_MAX_CHARS = 1000


def _message(row):
    return {k: row[k] for k in ("id", "sender", "recipient", "text", "created_at")}


def send_message(path, sender, recipient, text):
    if not isinstance(text, str) or not text.strip():
        raise PaymentError("Napiš nějakou zprávu")
    text = text.strip()
    if len(text) > MESSAGE_MAX_CHARS:
        raise PaymentError(f"Zpráva může mít nejvýš {MESSAGE_MAX_CHARS} znaků")
    _check_pair(sender, recipient, unknown="Neznámý příjemce", self_msg="Nelze psát sám sobě")
    created_at = _now()
    with _connect(path) as conn:
        cur = conn.execute(
            "INSERT INTO messages (sender, recipient, text, created_at) VALUES (?, ?, ?, ?)",
            (sender, recipient, text, created_at),
        )
    return {"id": cur.lastrowid, "sender": sender, "recipient": recipient, "text": text, "created_at": created_at}


def conversation(path, me, other, limit=200):
    """The last `limit` messages between two people, oldest first."""
    with _connect(path) as conn:
        rows = conn.execute(
            "SELECT * FROM messages WHERE (sender = ? AND recipient = ?) OR (sender = ? AND recipient = ?)"
            " ORDER BY created_at DESC, id DESC LIMIT ?",
            (me, other, other, me, limit),
        ).fetchall()
    return [_message(r) for r in reversed(rows)]


def chats(path, me):
    """One entry per friend with the last message (or None), newest conversation first."""
    out = []
    with _connect(path) as conn:
        for other, name in PEOPLE.items():
            if other == me:
                continue
            row = conn.execute(
                "SELECT * FROM messages WHERE (sender = ? AND recipient = ?) OR (sender = ? AND recipient = ?)"
                " ORDER BY created_at DESC, id DESC LIMIT 1",
                (me, other, other, me),
            ).fetchone()
            out.append({"with": other, "name": name, "last": _message(row) if row else None})
    out.sort(key=lambda c: (c["last"]["created_at"], c["last"]["id"]) if c["last"] else ("", 0), reverse=True)
    return out
