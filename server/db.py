"""SQLite storage for the simple payments of the four mockup people."""

import sqlite3
from contextlib import contextmanager
from datetime import datetime

PEOPLE = {1: "Person 1", 2: "Person 2", 3: "Person 3", 4: "Person 4"}
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
        for pid, name in PEOPLE.items():
            conn.execute(
                "INSERT OR IGNORE INTO accounts (id, name, balance) VALUES (?, ?, ?)",
                (pid, name, START_BALANCE),
            )


def reset_db(path):
    init_db(path)
    with _connect(path) as conn:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("DELETE FROM payments")
        conn.execute("UPDATE accounts SET balance = ?", (START_BALANCE,))
        conn.execute("COMMIT")


def get_balance(path, person_id):
    with _connect(path) as conn:
        row = conn.execute("SELECT balance FROM accounts WHERE id = ?", (person_id,)).fetchone()
    if row is None:
        raise PaymentError(f"Unknown person {person_id}")
    return row["balance"]


def send_payment(path, sender, recipient, amount, note=""):
    if type(amount) is not int or amount <= 0:
        raise PaymentError("Amount must be a whole number of CZK greater than zero")
    if sender not in PEOPLE or recipient not in PEOPLE:
        raise PaymentError("Unknown recipient")
    if sender == recipient:
        raise PaymentError("You can't pay yourself")
    note = (note or "").strip()
    created_at = datetime.now().isoformat(timespec="seconds")

    with _connect(path) as conn:
        conn.execute("BEGIN IMMEDIATE")
        try:
            balance = conn.execute(
                "SELECT balance FROM accounts WHERE id = ?", (sender,)
            ).fetchone()["balance"]
            if balance < amount:
                raise PaymentError("Insufficient funds")
            conn.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (amount, sender))
            conn.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (amount, recipient))
            cur = conn.execute(
                "INSERT INTO payments (sender, recipient, amount, note, created_at)"
                " VALUES (?, ?, ?, ?, ?)",
                (sender, recipient, amount, note, created_at),
            )
            conn.execute("COMMIT")
        except BaseException:
            conn.execute("ROLLBACK")
            raise

    return {
        "id": cur.lastrowid,
        "sender": sender,
        "recipient": recipient,
        "amount": amount,
        "note": note,
        "created_at": created_at,
    }


def history(path, person_id):
    with _connect(path) as conn:
        rows = conn.execute(
            "SELECT * FROM payments WHERE sender = ? OR recipient = ? ORDER BY id DESC",
            (person_id, person_id),
        ).fetchall()
    return [dict(r) for r in rows]
