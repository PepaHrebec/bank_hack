# Guided Demo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `uv run run.py --demo` serves one phone for David Vobecký with a blocking, step-by-step tour; every page load starts from a fresh database; the four teammates are in-server bots.

**Architecture:** A new `server/demo.py` adds David (id 5) to `db.PEOPLE`/`db.ACCOUNTS`, seeds his start state, and builds David's app from the normal `create_app` plus a `DemoOrchestrator` whose bots react to events pushed to ids 1–4 by calling their own in-process apps. Serving `/` in demo mode resets the database and injects `web/tour.js` + `web/tour.css`; the existing app gets only tiny, non-visual hooks.

**Tech Stack:** Python 3.14, FastAPI, httpx (ASGITransport, already a dependency via TestClient), SQLite; vanilla JS/CSS, no build step.

**Spec:** `docs/superpowers/specs/2026-11-28-guided-demo-design.md`

## Global Constraints

- Normal mode (`uv run run.py`, ports 3001–3004, `bank.db`) behaves exactly as before; `uv run pytest -q` stays green (825 tests at start).
- No visual change to the app; the only new UI is the tour layer.
- David Vobecký: id 5, account `5555555555/0800`, demo only.
- Demo database file default: `demo.db`; demo port: 3005 (`BASE_PORT + 5`).
- Tour copy is Czech. Values: step 2 Štěpán `1111111111/0800`; 2b Jirka 250 Kč „kino“; 2c Pepa 320 Kč „pizza“; 3 group „Chata“ with all four, expense 4 000 Kč „ubytování“ (800 Kč each); 4 card „Lokál“ 1 240 Kč, Štěpán's bot card „Benzina“ 1 600 Kč; 5 „Shrň mi minulý měsíc“; 6 to Jirka „Dlužíš mi 450 za lístky“.
- Bot reaction delay: 1.2 s (configurable, 0 in tests).
- Every tour step that waits on a bot or the model shows „Pokračovat“ after 12 s.

## Review Focus

- Refresh in the middle of a bot's delay: the old bot task must not act on the fresh database (Task 2 test `test_reset_cancels_pending_bot_actions`).
- A second tab / reconnect: reset happens only on `GET /`, never on `/api/state` or the websocket (Task 3 test `test_state_does_not_reset`).
- David typing a wrong account or amount: app validation shows its message and the tour stays on the step (Task 5 manual check list).
- Geoff hook returns nothing (no key, timeout): step 6 offers „Pokračovat“ (Task 5 manual check list).
- Banner auto-hide (4 s) while the tour waits for David to tap a notification action: banners are held while the tour targets them (Task 4).

---

### Task 1: David and his start state

**Files:**
- Create: `server/demo.py`
- Test: `tests/test_demo.py`

**Interfaces:**
- Produces: `demo.DAVID = 5`; `demo.add_david() -> None` (idempotent; adds `5: "David Vobecký"` to `db.PEOPLE` and `5: "5555555555/0800"` to `db.ACCOUNTS`, mutating the dicts in place so every module's `db.PEOPLE` sees it); `demo.seed_demo(path: str, now: datetime | None = None) -> None` (calls `db.reset_db`, then writes David's 90 days of salary + card payments via `seed._time_on`, `seed._card_amount`, `seed.BUSINESSES`, `seed._write`; plus a short WhatsApp history between 5 and 2 ending > 1 h before `now`).

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_demo.py
from datetime import datetime
import pytest
from server import db, demo

@pytest.fixture
def path(tmp_path):
    demo.add_david()
    p = str(tmp_path / "d.db")
    db.init_db(p)
    return p

def test_add_david_idempotent():
    demo.add_david(); demo.add_david()
    assert db.PEOPLE[5] == "David Vobecký"
    assert db.ACCOUNTS[5] == "5555555555/0800"
    assert db.person_by_account("5555555555/0800") == 5
    assert db.person_by_account("5555555555/0100") is None

def test_seed_gives_david_history_only(path):
    demo.seed_demo(path, now=datetime(2026, 11, 28, 12, 0))
    h = db.history(path, 5)
    assert len(h) > 50
    assert any(x.get("note") == "Výplata" for x in h)
    for p in (1, 2, 3, 4):
        assert db.history(path, p) == []
        assert db.get_balance(path, p) == db.START_BALANCE
    assert db.friends_of(path, 5) == []
    assert db.groups_for(path, 5) == [] and db.open_requests_for(path, 5) == []
    assert [m["sender"] for m in db.conversation(path, 5, 2)]  # history with Jirka exists

def test_seed_twice_is_identical(path):
    now = datetime(2026, 11, 28, 12, 0)
    demo.seed_demo(path, now=now); first = db.history(path, 5)
    db.send_payment(path, 5, 1, 10)
    demo.seed_demo(path, now=now)
    assert db.history(path, 5) == first
```

- [ ] **Step 2: Run** `uv run pytest tests/test_demo.py -q` — Expected: FAIL, `ImportError` / no module `server.demo`.
- [ ] **Step 3: Implement `add_david`, `seed_demo` in `server/demo.py`.** Seed with a fixed `random.Random(11)`; salaries on day 10 of each month (as `seed._build_events`), ~120 card payments, two of them today. Messages: 3–4 lines between 5 and 2 about going to a concert (no money amounts). Note: `test_seed_twice_is_identical` relies on `_write` resetting `sqlite_sequence`.
- [ ] **Step 4: Run** `uv run pytest tests/test_demo.py -q` — Expected: 3 passed. Then `uv run pytest -q` — Expected: all pass (adding id 5 must not leak into other tests: if it does, make `tests/test_demo.py` remove David again in a fixture teardown via `demo.remove_david()` and add that function).
- [ ] **Step 5: Commit** `git add server/demo.py tests/test_demo.py && git commit -m "feat(demo): David Vobecký and his start state"`

### Task 2: Bots

**Files:**
- Modify: `server/demo.py`
- Test: `tests/test_demo_bots.py`

**Interfaces:**
- Consumes: `demo.add_david`, `demo.DAVID`, `server.app.create_app`, `server.orchestrator.Orchestrator`.
- Produces: `class DemoOrchestrator(Orchestrator)` with `__init__(self, db_path: str, delay: float = 1.2)`, `bots: dict[int, httpx.AsyncClient]` (ids 1–4, each an `AsyncClient(transport=ASGITransport(create_app(i, self, db_path)), base_url="http://bot")`), `async send(person_id, event)` (calls `super().send`, then for ids 1–4 schedules a reaction), `cancel_all() -> None` (cancels pending bot tasks), `async bot_request(requester: int, amount, note: str) -> dict` (the bot POSTs `/api/requests` `{payer: 5, amount, note}` with no delay).
- Reactions (after `delay`): `friend_request` → POST `/api/friends/requests/{event["from_id"]}/accept`; `group_invite` → POST `/api/groups/{event["group"]["id"]}/accept`; `session_invite` → POST `/api/recording/invites/{event["starter"]}/accept`; `request_received` → POST `/api/requests/{event["request"]["id"]}/pay`. Plus: on `card_payment` sent to 5 with `event["recording"]` truthy, if person 1 is a participant of David's running session and has not yet paid in it, bot 1 POSTs `/api/card-payments` `{amount: 1600, note: "Benzina"}` (once per session).

- [ ] **Step 1: Write the failing tests** (TestClient for David over a `DemoOrchestrator(path, delay=0)`; helper `wait_for(fn, timeout=2)` polls every 20 ms):
  - `test_friend_request_accepted`: POST `/api/friends` `{"account": "1111111111/0800"}` → eventually `state["friends"]` contains id 1.
  - `test_group_invites_accepted_and_shares_paid`: befriend 1–4, POST `/api/groups` `{"name": "Chata", "members": [1,2,3,4]}`, wait until group's `invited == []`, POST expense `{"amount": 4000, "description": "ubytování"}`, approve → eventually David's balance rose by 3 200 and every `requested` row is `paid`.
  - `test_bot_pays_manual_request`: POST `/api/requests` `{"payer": 2, "amount": 250, "note": "kino"}` → eventually paid.
  - `test_session_invite_and_stepan_pays_once`: befriend 1, POST `/api/recording/start` `{"invite": [1]}` → eventually participants `[5, 1]`; two POST `/api/card-payments` → stop returns payments from both 5 and 1, exactly one with note „Benzina“.
  - `test_reset_cancels_pending_bot_actions`: orchestrator with `delay=0.3`; send friend request; immediately `orch.cancel_all()` + `demo.seed_demo(path)`; sleep 0.5 → no friends, no friend requests.
- [ ] **Step 2: Run** `uv run pytest tests/test_demo_bots.py -q` — Expected: FAIL (`DemoOrchestrator` missing).
- [ ] **Step 3: Implement `DemoOrchestrator`.** Keep task handles in a set; `cancel_all` cancels and clears it. Bot failures are logged, never raised.
- [ ] **Step 4: Run** `uv run pytest tests/test_demo_bots.py -q` — Expected: 5 passed; then `uv run pytest -q` all pass.
- [ ] **Step 5: Commit** `git commit -m "feat(demo): teammates as bots that accept and pay"`

### Task 3: Demo app and `run.py --demo`

**Files:**
- Modify: `server/demo.py`, `run.py`, `README.md`
- Test: `tests/test_demo_app.py`

**Interfaces:**
- Consumes: Tasks 1–2.
- Produces: `demo.create_demo_app(db_path: str, delay: float = 1.2) -> FastAPI` — calls `add_david()`, `db.init_db`, builds `DemoOrchestrator`, `app = create_app(5, orch, db_path)`; replaces the `/` route (remove it from `app.router.routes`, add a new one) with one that does `orch.cancel_all()`, `seed_demo(db_path)` and returns `index.html` with `<link rel="stylesheet" href="/static/tour.css">` inserted before `</head>` and `<script src="/static/tour.js"></script>` before `</body>`; adds `POST /api/demo/bot-request` (body `{"from": 1..4, "amount", "note"}` → `orch.bot_request`, 400 on bad `from`). `run.py --demo` serves only this app on `base_port + 5`, default db `demo.db`, and prints `David Vobecký (demo): http://<host>:3005`.

- [ ] **Step 1: Write the failing tests**
  - `test_index_resets_and_injects_tour`: make a payment from 5, GET `/` → body contains `tour.js` and `tour.css`; state shows fresh history (no payment to 1) and no friends.
  - `test_state_does_not_reset`: after GET `/`, add a friend request; GET `/api/state` twice → request still there.
  - `test_bot_request_endpoint`: POST `/api/demo/bot-request` `{"from": 3, "amount": 320, "note": "pizza"}` → 200, `to_pay` has it; `{"from": 5, ...}` → 400.
  - `test_normal_app_has_no_demo_routes`: `create_app(1, Orchestrator(), path)` → POST `/api/demo/bot-request` is 404 and `/` has no `tour.js`.
- [ ] **Step 2: Run** `uv run pytest tests/test_demo_app.py -q` — Expected: FAIL.
- [ ] **Step 3: Implement `create_demo_app` and the `--demo` flag in `run.py`;** README gets a short "Demo" section (command, port, refresh = restart).
- [ ] **Step 4: Run** `uv run pytest -q` — Expected: all pass. Then `uv run run.py --demo` starts and `curl -s localhost:3005/ | grep tour.js` prints the script tag.
- [ ] **Step 5: Commit** `git commit -m "feat(demo): run.py --demo serves David's phone, reset on every page load"`

### Task 4: Hooks the tour needs in the existing front end

**Files:**
- Modify: `web/phone.js`, `web/app.js`

**Interfaces:**
- Produces (all no-ops for the normal app):
  - `Phone.colors[5]` = `"#8e5cf7"`.
  - `Phone.holdBanners(on: boolean)` — while on, banners don't auto-hide; turning it off lets held banners hide after the usual 4 s.
  - `app.js` dispatches `document.dispatchEvent(new CustomEvent("geoff:state", {detail: state}))` at the end of every `refresh()`, and `new CustomEvent("geoff:view", {detail: name})` in `show(name)`.

No automated JS tests exist in this repo; verification is by browser.

- [ ] **Step 1: Implement the three hooks** (a few lines each).
- [ ] **Step 2: Verify** `uv run pytest -q` passes, and in normal mode (`uv run run.py`, open :3001) the app works and the console shows no errors; in the console, `document.addEventListener("geoff:view", e => console.log(e.detail))` logs view names when navigating.
- [ ] **Step 3: Commit** `git commit -m "feat: state/view events and holdBanners for the demo tour"`

### Task 5: The tour

**Files:**
- Create: `web/tour.js`, `web/tour.css`

**Interfaces:**
- Consumes: `geoff:state`, `geoff:view`, `Phone.onEvent`, `Phone.openApp`, `Phone.holdBanners`, `POST /api/demo/bot-request`.

**Engine (decided):**
- A step is `{text, target: () => Element[] , done: (ctx) => boolean, enter?: () => void, wait?: boolean}`; `ctx` holds the latest state, the current view, which app window is open, and the last few pushed events. The engine re-checks `done` on every `geoff:state`, `geoff:view`, pushed event, and DOM mutation of `#screen` (MutationObserver), and advances when true.
- Targets are found by selector + visible text (e.g. `.big-btn` with text „Přátelé“), never by new ids in `app.js`.
- Blocking: capture-phase listeners on `document` for `pointerdown`, `click`, `keydown`, `focusin`, `input`, `submit` stop anything whose target is not inside a current target element or the bubble. Inputs inside a target popup/form are allowed.
- Highlight: a fixed ring over the first target's rect (box-shadow dim around it), repositioned every animation frame; the bubble sits below or above it inside the viewport; on narrow screens it may overlap the phone edge.
- `wait: true` steps show „Pokračovat“ after 12 s, which advances.
- Card steps (welcome, vision, done) are a centered card with one button.
- While a step targets a notification, `Phone.holdBanners(true)`; otherwise false. If the banner is gone, the step's target falls back to the notification in the pull-down list and the bubble says to pull down from the top.
- After the last step the layer and all listeners are removed.

**Steps (order and completion):**

| # | Bubble (gist) | Target(s) | Done when |
|---|---------------|-----------|-----------|
| 0 | Welcome, David | card button „Začít“ | clicked |
| 1a | Your balance and today's change; tap to see history | `.balance-card` | view `history` |
| 1b | Back | `.back-btn` in history | view `main` |
| 1c | Pay to any Czech account | „Zaplatit“ tile | view `accountPay` |
| 1d | Type 5555555555, bank Komerční banka, 500 Kč, „za kolo“ | the account-pay form | history contains an account payment of 500 |
| 1e | Show the QR screen | „QR kód“ tile, then its back button | view `qr`, then `main` |
| 2a | Friends are Geoff users; open Přátelé | „Přátelé“ tile | view `contacts` |
| 2b | Add Štěpán: 1111111111/0800 | „Přidat přítele“, then popup input + „Přidat“ | friend request to 1 sent (`friend_requests_sent`) |
| 2c | Štěpán is accepting… (wait) | — | `friends` contains 1 |
| 2d | „Přidat zbytek“ (bubble button; tour POSTs `/api/friends` for 2, 3, 4) | bubble button | `friends` contains 1–4 |
| 2e | Ask Jirka for money: tap Jirka, switch to Žádost, 250 Kč „kino“, Vyžádat | Jirka's row, then the pay form | a request to 2 for 250 is `paid` (wait) |
| 2f | Pepa asks you for money (tour POSTs bot-request from 3, 320, „pizza“ on enter); open K zaplacení | „K zaplacení“ | view `tobepaid` |
| 2g | Pay Pepa: Zaplatit → Potvrdit platbu | Pepa's request row, then confirm buttons | that request is paid (no longer in `to_pay`) |
| 3a | Group settle: open Skupinové vyrovnání → Nová skupina | quick action, then „Nová skupina“ | view `newgroup` |
| 3b | Name „Chata“, tick all four, Vytvořit skupinu | the new-group form | a group „Chata“ exists |
| 3c | Waiting for everyone to accept (wait) | — | that group's `invited` is empty |
| 3d | Add 4 000 Kč „ubytování“ | expense form | group total 4 000 |
| 3e | Approve: equal split, everyone owes 800 Kč | approve button | group approved |
| 3f | Watch them pay (wait) | — | all four group requests paid |
| 4a | Go home (bubble button calls `Phone.openApp(null)`) | bubble button | home screen open |
| 4b | Spustit skupinovou platbu on the widget | widget toggle | start popup open |
| 4c | Invite only Štěpán, Spustit | popup's Štěpán checkbox + „Spustit“ | `recording` running with 1 invited or joined |
| 4d | Štěpán joins (wait) | — | `recording.participants` includes 1 |
| 4e | Pay by card: the 💳 chip, prefilled Lokál 1 240 | `#demoAside` chip, form | a card payment of 1 240 in recording |
| 4f | Štěpán is paying too (David's own `recording` shows only his payments; Štěpán's appears in the stop popup) | — | 3 s after 4e |
| 4g | Ukončit skupinovou platbu | widget toggle | stop popup open |
| 4h | Vytvořit skupinové vyrovnání | popup button | a new group exists from the session |
| 5a | Ask Geoff: open the app's chat, type „Shrň mi minulý měsíc“, send | chat input + send | a reply bubble appears (wait) |
| 6a | Vision card | card button | clicked |
| 6b | Go home → WhatsApp | bubble button home, then WhatsApp dock icon | WhatsApp open |
| 6c | Open Jirka's chat, send „Dlužíš mi 450 za lístky“ | Jirka row, compose form | message sent |
| 6d | Geoff noticed: tap Potvrdit | the Geoff suggestion's „Potvrdit“ | a request to 2 for 450 exists (wait) |
| 7 | Done card | card button | layer removed |

Bubble copy is the builder's, in Czech, short (one or two lines), tykání, gender-neutral.

- [ ] **Step 1: Build the engine** with steps 0 and 1a–1b only; run `uv run run.py --demo`, open `http://localhost:3005`, check: other taps are blocked, the ring follows the target, refresh restarts.
- [ ] **Step 2: Add steps 1c–2g;** click through; check typing a wrong account in 2b shows the app's error and the step stays.
- [ ] **Step 3: Add steps 3a–4h;** click through.
- [ ] **Step 4: Add steps 5a–7;** click through the whole tour twice (second time after a refresh mid-tour), and once with `OPENROUTER_API_KEY` unset to see „Pokračovat“ in 5a and 6d.
- [ ] **Step 5: Run** `uv run pytest -q` — Expected: all pass. **Commit** `git add web/tour.js web/tour.css && git commit -m "feat(demo): guided tour layer"`
