"""SQLite storage for the payments and payment requests of the four mockup people."""

import sqlite3
from contextlib import contextmanager
from datetime import datetime

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
            " status TEXT NOT NULL DEFAULT 'open',"  # open | paid | declined
            " payment_id INTEGER REFERENCES payments(id),"
            " created_at TEXT NOT NULL)"
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
        conn.execute("DELETE FROM payments")
        conn.execute("UPDATE accounts SET balance = ?", (START_BALANCE,))
        conn.execute("COMMIT")


def get_balance(path, person_id):
    with _connect(path) as conn:
        row = conn.execute("SELECT balance FROM accounts WHERE id = ?", (person_id,)).fetchone()
    if row is None:
        raise PaymentError(f"Unknown person {person_id}")
    return row["balance"]


def _now():
    return datetime.now().isoformat(timespec="seconds")


def _check_amount(amount):
    if type(amount) is not int or amount <= 0:
        raise PaymentError("Amount must be a whole number of CZK greater than zero")


def _check_pair(me, other, unknown="Unknown recipient", self_msg="You can't pay yourself"):
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


def _transfer(conn, sender, recipient, amount, note):
    """Move money inside an open transaction and record the payment."""
    balance = conn.execute("SELECT balance FROM accounts WHERE id = ?", (sender,)).fetchone()["balance"]
    if balance < amount:
        raise PaymentError("Insufficient funds")
    conn.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (amount, sender))
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


def history(path, person_id):
    with _connect(path) as conn:
        rows = conn.execute(
            "SELECT * FROM payments WHERE sender = ? OR recipient = ? ORDER BY id DESC",
            (person_id, person_id),
        ).fetchall()
    return [dict(r) for r in rows]


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
    _check_pair(requester, payer, "Unknown contact", "You can't request money from yourself")
    with _transaction(path) as conn:
        return _insert_request(conn, requester, payer, amount, (note or "").strip())


def create_group_request(path, requester, title, shares, note=""):
    """One request per payer in `shares` ({payer_id: amount}), grouped under `title`."""
    if not shares:
        raise PaymentError("Pick at least one person")
    for payer, amount in shares.items():
        _check_amount(amount)
        _check_pair(requester, payer, "Unknown contact", "You can't request money from yourself")
    title = (title or "").strip() or "Group payment"
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
        "SELECT payer, amount, status FROM requests WHERE group_id = ? ORDER BY id", (group_id,)
    ).fetchall()
    return {
        "id": g["id"],
        "title": g["title"],
        "requester": g["requester"],
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
        raise PaymentError("Request not found")
    if r["status"] != "open":
        raise PaymentError(f"This request is already {r['status']}")
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
