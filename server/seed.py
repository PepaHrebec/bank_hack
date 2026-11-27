"""Czech mock data: three months of salaries, card payments and friend transfers for the four people."""

import random
from datetime import datetime, timedelta

from . import db

DAYS = 90
CARDS_PER_PERSON = 160
TRANSFERS_PER_PAIR = 24  # each person is in 3 pairs: ~72 transfers vs ~163 other items, i.e. ~30 %
SALARY_RANGE = (32000, 48000)

# (note, min, max) in whole Kč; most are rounded to 10 Kč below
BUSINESSES = [
    ("Albert", 120, 1400), ("Lidl", 150, 1500), ("Kaufland", 200, 2200), ("Billa", 100, 1200),
    ("Penny Market", 80, 900), ("Tesco", 150, 1800), ("Rohlik.cz", 500, 2600),
    ("Lokál", 250, 900), ("Pivovarský dům", 280, 950), ("U Fleků", 300, 1100),
    ("Bageterie Boulevard", 90, 250), ("Ugo", 60, 180), ("Costa Coffee", 70, 190),
    ("Café Louvre", 120, 480), ("Dámejídlo", 200, 700), ("Wolt", 220, 780), ("Bolt", 90, 420),
    ("Lítačka DPP", 40, 550), ("České dráhy", 80, 780), ("RegioJet", 150, 690),
    ("Benzina", 700, 1900), ("Shell", 650, 2000), ("Lékárna Dr.Max", 60, 650),
    ("dm drogerie", 100, 900), ("Rossmann", 90, 800), ("Alza.cz", 250, 6500),
    ("Datart", 400, 9000), ("Kino Lucerna", 190, 520), ("Sportisimo", 400, 3200),
    ("Decathlon", 250, 2800), ("Knihy Dobrovský", 150, 900), ("Potrefená husa", 250, 900),
    ("Manifesto Market", 140, 450),
]

TRANSFER_NOTES = [
    "pivo", "oběd", "pizza", "lístky na koncert", "benzín", "dárek pro Janu", "Netflix",
    "nájem – podíl", "kafe", "taxík", "večeře", "jízdenky", "Spotify", "víno", "nákup",
    "půjčka", "hospoda", "kino", "snídaně", "dárek", "", "", "",
]

REQUESTS = [  # (requester, payer, amount, note)
    (2, 1, 450, "lístky na koncert"),
    (3, 2, 180, "oběd v Lokálu"),
    (4, 3, 1200, "nájem – podíl"),
    (1, 4, 320, "pizza"),
]

GROUP_NAME = "Chata Krkonoše"
GROUP_EXPENSES = [  # (payer, amount, description)
    (3, 6400, "ubytování"),
    (1, 1850, "nákup jídla"),
    (4, 1200, "benzín"),
]

DAY_START = (7, 0)
DAY_END = (23, 30)


def _time_on(rng, day, now):
    """A random time on `day` between 07:00 and 23:30, never later than `now`."""
    start = day.replace(hour=DAY_START[0], minute=DAY_START[1], second=0, microsecond=0)
    end = min(day.replace(hour=DAY_END[0], minute=DAY_END[1], second=0, microsecond=0), now)
    if end <= start:
        return end
    return start + timedelta(seconds=rng.randrange(int((end - start).total_seconds()) + 1))


def _card_amount(rng, low, high):
    # Skewed towards the cheap end, like real shopping; rounded to 10 Kč except small ones.
    amount = int(low + (high - low) * rng.random() ** 2)
    return amount if amount < 100 else amount // 10 * 10


def _build_events(rng, now):
    """All events as (datetime, kind, data), unsorted."""
    first_day = (now - timedelta(days=DAYS - 1)).replace(hour=0, minute=0, second=0, microsecond=0)
    days = [first_day + timedelta(days=i) for i in range(DAYS)]
    today = days[-1]
    events = []

    for person in db.PEOPLE:
        for day in days:
            if day.day == 10:
                events.append((_time_on(rng, day, now), "income",
                               (person, rng.randrange(SALARY_RANGE[0], SALARY_RANGE[1] + 1, 100), "Výplata")))
        for i in range(CARDS_PER_PERSON):
            # the first two are today's, so the "today's change" line always has something to show
            day = today if i < 2 else rng.choice(days)
            note, low, high = rng.choice(BUSINESSES)
            events.append((_time_on(rng, day, now), "card", (person, _card_amount(rng, low, high), note)))

    pairs = [(a, b) for a in db.PEOPLE for b in db.PEOPLE if a < b]
    for a, b in pairs:
        for i in range(TRANSFERS_PER_PAIR):
            sender, recipient = (a, b) if rng.random() < 0.5 else (b, a)
            day = today if i == 0 else rng.choice(days)
            amount = rng.choice([50, 80, 100, 120, 150, 200, 250, 300, 350, 400, 500, 800, 1000, 1500])
            events.append((_time_on(rng, day, now), "transfer",
                           (sender, recipient, amount, rng.choice(TRANSFER_NOTES))))
    return events


def _write(path, events):
    """Insert the events oldest first, dropping any debit the account could not cover."""
    balances = {p: db.START_BALANCE for p in db.PEOPLE}
    with db._transaction(path) as conn:
        # restart ids at 1 so seeding twice gives identical rows
        conn.execute("DELETE FROM sqlite_sequence WHERE name IN ('payments', 'card_payments', 'income')")
        for when, kind, data in sorted(events, key=lambda e: e[0]):
            stamp = when.isoformat(timespec="seconds")
            if kind == "income":
                person, amount, note = data
                balances[person] += amount
                conn.execute("INSERT INTO income (person, amount, note, created_at) VALUES (?, ?, ?, ?)",
                             (person, amount, note, stamp))
            elif kind == "card":
                person, amount, note = data
                if balances[person] < amount:
                    continue
                balances[person] -= amount
                conn.execute("INSERT INTO card_payments (person, amount, note, created_at) VALUES (?, ?, ?, ?)",
                             (person, amount, note, stamp))
            else:
                sender, recipient, amount, note = data
                if balances[sender] < amount:
                    continue
                balances[sender] -= amount
                balances[recipient] += amount
                conn.execute(
                    "INSERT INTO payments (sender, recipient, amount, note, created_at) VALUES (?, ?, ?, ?, ?)",
                    (sender, recipient, amount, note, stamp))
        for person, balance in balances.items():
            conn.execute("UPDATE accounts SET balance = ? WHERE id = ?", (balance, person))


def seed_db(path, now=None, rng_seed=7):
    """Wipe the database and fill it with mock data; returns {person id: number of history items}."""
    now = (now or datetime.now()).replace(microsecond=0)
    db.reset_db(path)
    _write(path, _build_events(random.Random(rng_seed), now))

    for requester, payer, amount, note in REQUESTS:
        db.create_request(path, requester, payer, amount, note)
    (creator, amount, description), *others = GROUP_EXPENSES
    group = db.create_group(path, creator, GROUP_NAME, [1, 4], {"amount": amount, "description": description})
    for payer, amount, description in others:
        db.add_expense(path, group["id"], payer, amount, description)

    return {p: len(db.history(path, p)) for p in db.PEOPLE}
