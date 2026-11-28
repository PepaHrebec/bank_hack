"""The guided demo: one phone for David Vobecký, a fresh database on every page load, the four
teammates as bots. Many visitors at once: each page load is its own session with its own database.

David exists only in demo mode: `add_david` puts him into `db.PEOPLE` / `db.ACCOUNTS` (the same dict
objects every module reads), so the normal four-phone mode never sees him.
"""

import asyncio
import glob
import logging
import os
import random
import secrets
import time
from datetime import datetime, timedelta

import httpx
from fastapi import Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool
from starlette.requests import HTTPConnection

from server import db, seed
from server.app import WEB_DIR, create_app
from server.orchestrator import Orchestrator

log = logging.getLogger("geoff.demo")

DAVID = 5
DAVID_NAME = "David Vobecký"
BOTS = (1, 2, 3, 4)
BOT_DELAY = 1.2  # seconds, so it looks like someone tapping on their phone
STEPAN_CARD = {"amount": 460, "note": "Taxi"}
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
COOKIE = "geoff_demo"
EXPIRED = "Ukázka vypršela. Obnov stránku a začni znovu."
MAX_SESSIONS = 50
IDLE_SECS = 30 * 60
CHAT_LIMIT = 15  # questions to the chatbot per session (each one costs a model call)
MESSAGE_LIMIT = 30  # WhatsApp messages per session (each can cost a Geoff-hook model call)


def _session_app(db_path, delay):
    """One visitor's demo: David's normal app over their own database, the bots, the bot-request route."""
    orch = DemoOrchestrator(db_path, delay)
    app = create_app(DAVID, orch, db_path)

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

    return app, orch


def _fresh_db(path):
    db.init_db(path)
    seed_demo(path)


class Session:
    def __init__(self, sid, path, app, orch, now):
        self.sid, self.path, self.app, self.orch = sid, path, app, orch
        self.last_seen = now
        self.chats = 0
        self.messages = 0


class DemoHub:
    """The demo for many visitors at once: every page load gets its own session (a cookie), with its
    own SQLite file, bots and app. Requests are passed to the session the cookie names; the static
    files are shared. Idle sessions are dropped, and at most `max_sessions` run at once."""

    def __init__(self, root, delay=BOT_DELAY, max_sessions=MAX_SESSIONS, idle_secs=IDLE_SECS,
                 chat_limit=CHAT_LIMIT, message_limit=MESSAGE_LIMIT, clock=time.monotonic):
        add_david()
        self.root = root
        os.makedirs(root, exist_ok=True)
        self.delay, self.max_sessions, self.idle_secs = delay, max_sessions, idle_secs
        self.chat_limit, self.message_limit, self.clock = chat_limit, message_limit, clock
        self.sessions = {}
        self.static = StaticFiles(directory=WEB_DIR)
        page = (WEB_DIR / "index.html").read_text(encoding="utf-8")
        self.page = page.replace("</head>", f"  {TOUR_CSS}\n</head>").replace("</body>", f"  {TOUR_JS}\n</body>")

    # ---- sessions ----

    async def _new_session(self):
        # The bookkeeping stays on the event loop, so two visitors arriving at once can't race;
        # only building the database goes to a thread.
        now = self.clock()
        for s in [s for s in self.sessions.values() if now - s.last_seen > self.idle_secs]:
            self._drop(s.sid)
        while len(self.sessions) >= self.max_sessions:
            self._drop(min(self.sessions.values(), key=lambda s: s.last_seen).sid)
        sid = secrets.token_urlsafe(16)
        path = os.path.join(self.root, f"{sid}.db")
        await run_in_threadpool(_fresh_db, path)
        app, orch = _session_app(path, self.delay)
        self.sessions[sid] = Session(sid, path, app, orch, now)
        return sid

    def _drop(self, sid):
        s = self.sessions.pop(sid, None)
        if s is None:
            return
        s.orch.cancel_all()
        for f in glob.glob(glob.escape(s.path) + "*"):  # the db and any -journal / -wal next to it
            try:
                os.remove(f)
            except OSError:
                pass

    # ---- ASGI ----

    async def __call__(self, scope, receive, send):
        if scope["type"] == "lifespan":
            while True:
                message = await receive()
                if message["type"] == "lifespan.startup":
                    await send({"type": "lifespan.startup.complete"})
                elif message["type"] == "lifespan.shutdown":
                    for sid in list(self.sessions):
                        self._drop(sid)
                    await send({"type": "lifespan.shutdown.complete"})
                    return
        path = scope["path"]
        if path.startswith("/static/"):
            return await self.static({**scope, "path": path[len("/static"):], "root_path": "/static"}, receive, send)
        old = HTTPConnection(scope).cookies.get(COOKIE)
        if scope["type"] == "http" and path == "/":
            # Every page load is a fresh start: a new session replaces this browser's old one.
            # Only "/" does this; /api/state and websocket reconnects of a running tab must not.
            self._drop(old)
            sid = await self._new_session()
            response = HTMLResponse(self.page, headers={"Cache-Control": "no-store"})
            response.set_cookie(COOKIE, sid, httponly=True, samesite="lax")
            return await response(scope, receive, send)
        session = self.sessions.get(old)
        if session is None:
            if scope["type"] == "websocket":
                return await send({"type": "websocket.close", "code": 4410})
            return await JSONResponse({"detail": EXPIRED}, status_code=410)(scope, receive, send)
        session.last_seen = self.clock()
        if scope["type"] == "http" and scope["method"] == "POST":
            limited = self._limit(session, path)
            if limited:
                return await JSONResponse({"detail": limited}, status_code=429)(scope, receive, send)
        await session.app(scope, receive, send)

    def _limit(self, session, path):
        """A message if this request goes over the session's limit, else None (and it's counted)."""
        if path == "/api/chat":
            if session.chats >= self.chat_limit:
                return f"V ukázce je limit {self.chat_limit} otázek. Obnov stránku a začni znovu."
            session.chats += 1
        elif path == "/api/messages":
            if session.messages >= self.message_limit:
                return f"V ukázce je limit {self.message_limit} zpráv. Obnov stránku a začni znovu."
            session.messages += 1
        return None


def create_demo_app(root, delay=BOT_DELAY, **limits):
    """The demo server: a DemoHub keeping one session per visitor under `root`."""
    return DemoHub(root, delay, **limits)
