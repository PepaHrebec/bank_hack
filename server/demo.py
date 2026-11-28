"""The guided demo: one phone for David Vobecký, a fresh database on every page load, the four
teammates as bots.

David exists only in demo mode: `add_david` puts him into `db.PEOPLE` / `db.ACCOUNTS` (the same dict
objects every module reads), so the normal four-phone mode never sees him.
"""

import random
from datetime import datetime, timedelta

from server import db, seed

DAVID = 5
DAVID_NAME = "David Vobecký"
DAYS = 90
CARDS = 120

# (hours before `now`, sender, text), oldest first: small talk with Jirka, no money in it.
JIRKA_CHAT = [
    (50, 2, "Čau Davide, jdeš v sobotu na ten koncert?"),
    (49.5, DAVID, "Jasně, už se těším"),
    (49, 2, "Lístky vezmu já, pak se vyrovnáme"),
    (3, 2, "Tak co, jak se ti líbilo?"),
]


def add_david():
    """Add David to the people and accounts (idempotent)."""
    db.PEOPLE[DAVID] = DAVID_NAME
    db.ACCOUNTS[DAVID] = f"{str(DAVID) * 10}/{db.GEOFF_BANK}"


def remove_david():
    """Undo `add_david` (for tests that must leave the four people as they were)."""
    db.PEOPLE.pop(DAVID, None)
    db.ACCOUNTS.pop(DAVID, None)


def _events(rng, now):
    """David's salaries and card payments over the last DAYS days, as seed events."""
    first_day = (now - timedelta(days=DAYS - 1)).replace(hour=0, minute=0, second=0, microsecond=0)
    days = [first_day + timedelta(days=i) for i in range(DAYS)]
    events = []
    for day in days:
        if day.day == 10:
            events.append((seed._time_on(rng, day, now), "income",
                           (DAVID, rng.randrange(38000, 46001, 100) * 100, "Výplata")))
    for i in range(CARDS):
        # the first two are today's, so "today's change" has something to show
        day = days[-1] if i < 2 else rng.choice(days)
        note, low, high = rng.choice(seed.BUSINESSES)
        events.append((seed._time_on(rng, day, now), "card", (DAVID, seed._card_amount(rng, low, high), note)))
    return events


def seed_demo(path, now=None):
    """Wipe the database and give it the demo's start state: David's own history, nothing else."""
    now = (now or datetime.now()).replace(microsecond=0)
    db.reset_db(path)
    seed._write(path, _events(random.Random(11), now))
    with db._transaction(path) as conn:
        conn.execute("DELETE FROM sqlite_sequence WHERE name = 'messages'")
        for hours, sender, text in JIRKA_CHAT:
            when = (now - timedelta(minutes=round(hours * 60))).isoformat(timespec="seconds")
            conn.execute("INSERT INTO messages (sender, recipient, text, created_at) VALUES (?, ?, ?, ?)",
                         (sender, 2 if sender == DAVID else DAVID, text, when))
