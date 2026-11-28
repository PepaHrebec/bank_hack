"""The guided demo: one phone for David Vobecký, a fresh database on every page load, the four
teammates as bots.

David exists only in demo mode: `add_david` puts him into `db.PEOPLE` / `db.ACCOUNTS` (the same dict
objects every module reads), so the normal four-phone mode never sees him.
"""

import asyncio
import logging
import random
from datetime import datetime, timedelta

import httpx
from fastapi import Request
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.routing import Route

from server import db, seed
from server.app import WEB_DIR, create_app
from server.orchestrator import Orchestrator

log = logging.getLogger("geoff.demo")

DAVID = 5
DAVID_NAME = "David Vobecký"
BOTS = (1, 2, 3, 4)
BOT_DELAY = 1.2  # seconds, so it looks like someone tapping on their phone
STEPAN_CARD = {"amount": 1600, "note": "Benzina"}
# What each teammate adds to a group they join (Štěpán adds nothing): mock shared costs.
BOT_EXPENSES = {
    2: {"amount": 1450, "description": "jídlo"},
    3: {"amount": 780, "description": "pití"},
    4: {"amount": 1120, "description": "benzín"},
}
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


class DemoOrchestrator(Orchestrator):
    """The normal relay, plus the four teammates as bots: whatever would reach their phones, they
    accept or pay, through their own in-process app, as if they had tapped it."""

    def __init__(self, db_path, delay=BOT_DELAY):
        super().__init__()
        self.db_path = db_path
        self.delay = delay
        self.bots = {
            i: httpx.AsyncClient(transport=httpx.ASGITransport(app=create_app(i, self, db_path)), base_url="http://bot")
            for i in BOTS
        }
        self.tasks = set()
        self.generation = 0  # bumped by cancel_all; a task from an older generation does nothing
        self.stepan_paid = set()  # sessions (by start time) Štěpán has already paid in

    async def send(self, person_id, event):
        await super().send(person_id, event)
        actions = self._reaction(person_id, event)
        if actions:
            task = asyncio.create_task(self._act(self.generation, actions))
            self.tasks.add(task)
            task.add_done_callback(self.tasks.discard)

    def _reaction(self, person_id, event):
        """What the bots do about an event: [(bot, path, json body)], one after another, or []."""
        kind = event.get("type")
        if person_id in BOTS:
            if kind == "friend_request":
                return [(person_id, f"/api/friends/requests/{event['from_id']}/accept", None)]
            if kind == "group_invite":
                gid = event["group"]["id"]
                actions = [(person_id, f"/api/groups/{gid}/accept", None)]
                if person_id in BOT_EXPENSES:
                    actions.append((person_id, f"/api/groups/{gid}/expenses", BOT_EXPENSES[person_id]))
                return actions
            if kind == "session_invite":
                return [(person_id, f"/api/recording/invites/{event['starter']}/accept", None)]
            if kind == "request_received":
                return [(person_id, f"/api/requests/{event['request']['id']}/pay", None)]
        elif person_id == DAVID and kind == "card_payment" and event.get("recording"):
            rec = db.recording(self.db_path, DAVID)
            if rec and 1 in rec["participants"] and rec["started_at"] not in self.stepan_paid:
                self.stepan_paid.add(rec["started_at"])
                return [(1, "/api/card-payments", STEPAN_CARD)]
        return []

    async def _act(self, generation, actions):
        """Run the actions in order, each after the bot's "tapping" delay."""
        for bot, url, body in actions:
            try:
                await asyncio.sleep(self.delay)
                if generation != self.generation:
                    return
                r = await self.bots[bot].post(url, json=body)
                if r.status_code != 200:
                    log.warning("Bot %s: %s -> %s %s", bot, url, r.status_code, r.text)
                    return
            except asyncio.CancelledError:
                return
            except Exception:
                log.exception("Bot %s failed on %s", bot, url)
                return

    def cancel_all(self):
        """Forget every pending bot action (the database is about to be reset)."""
        self.generation += 1
        self.stepan_paid.clear()
        for task in list(self.tasks):
            task.get_loop().call_soon_threadsafe(task.cancel)
        self.tasks.clear()

    async def bot_request(self, requester, amount, note):
        """Have a bot ask David for money right now; returns the bot app's response body."""
        r = await self.bots[requester].post("/api/requests", json={"payer": DAVID, "amount": amount, "note": note})
        if r.status_code != 200:
            raise db.PaymentError(r.json().get("detail", "Žádost se nepodařila"))
        return r.json()


TOUR_CSS = '<link rel="stylesheet" href="/static/tour.css">'
TOUR_JS = '<script src="/static/tour.js"></script>'


def create_demo_app(db_path, delay=BOT_DELAY):
    """David's phone: the normal app, whose page resets the database and brings the tour along."""
    add_david()
    db.init_db(db_path)
    orch = DemoOrchestrator(db_path, delay)
    app = create_app(DAVID, orch, db_path)

    # Every page load is a fresh start. Only "/" resets: /api/state and the websocket reconnect
    # are also hit by a tab that's already running.
    app.router.routes[:] = [r for r in app.router.routes if not (isinstance(r, Route) and r.path == "/")]

    @app.get("/")
    def index():
        orch.cancel_all()
        seed_demo(db_path)
        page = (WEB_DIR / "index.html").read_text(encoding="utf-8")
        page = page.replace("</head>", f"  {TOUR_CSS}\n</head>").replace("</body>", f"  {TOUR_JS}\n</body>")
        return HTMLResponse(page)

    @app.post("/api/demo/bot-request")
    async def bot_request(request: Request):
        try:
            body = await request.json()
            requester = body.get("from")
            if type(requester) is not int or requester not in BOTS:
                raise db.PaymentError("Neznámý přítel")
            return await orch.bot_request(requester, body.get("amount"), body.get("note", ""))
        except (ValueError, AttributeError, db.PaymentError) as e:
            return JSONResponse({"detail": str(e)}, status_code=400)

    return app
