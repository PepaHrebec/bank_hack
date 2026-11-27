# Four-Phone Bank Mockup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** One Python process serving four phone pages (ports 3001–3004), a hidden orchestrator relaying events over WebSockets, and an SQLite-backed simple-payments placeholder app.

**Architecture:** `run.py` starts four uvicorn servers in one asyncio loop. Each server is a FastAPI app built by `create_app(person_id, orchestrator, db_path)`; all four share one `Orchestrator` (in-memory map person → open WebSockets) and one SQLite file. The frontend is static HTML/CSS/JS: `phone.js` is the phone shell (frame, clock, banner, pull-down), `app.js` is the replaceable placeholder bank app.

**Tech Stack:** Python 3.14, FastAPI, uvicorn, stdlib sqlite3, pytest + FastAPI TestClient; plain HTML/CSS/JS.

**Spec:** `docs/superpowers/specs/2026-11-27-four-phone-mockup-design.md`

## Global Constraints

- Ports 3001–3004 = Person 1–4. One command starts everything: `python run.py`. `python run.py --reset` restores starting state and exits.
- Starting balance 10 000 CZK per person. Amounts whole CZK, > 0. No paying yourself. Insufficient balance → refused.
- Notification text: `"Person 1 sent you 250 CZK"` (note appended on a second line if present).
- Banner stays ~4 s; tap dismisses. Pull-down: time, 5 rising signal bars, notifications newest first, dashed placeholder slots when empty. Notifications not persisted.
- Realistic phone (bezel, notch, home bar), centred, scaled to window height, dark background, nothing else on the page.
- Frontend: no build step. `app.js` must only use the shell through `window.Phone.notify(...)` and `window.Phone.onEvent(...)` so it can be replaced.

## Review Focus

1. Amount given as string, float, 0, negative, or missing → 400 with message, no DB change. (Task 2 test)
2. Recipient unknown or equal to sender → 400. (Task 1/2 tests)
3. Two payments racing to overdraw → at most one succeeds; balance never negative. (Task 1 test: sequential double-spend; writes use `BEGIN IMMEDIATE`)
4. A closed/broken WebSocket in the orchestrator must not stop delivery to other sockets. (Task 2 test)
5. Same person open in two tabs → both receive the event. (Task 2 test)

---

### Task 1: Payments database

**Files:**
- Create: `requirements.txt`, `server/__init__.py`, `server/db.py`
- Test: `tests/test_db.py`

**Interfaces:**
- Produces (`server/db.py`):
  - `PEOPLE: dict[int, str]` = `{1: "Person 1", ..., 4: "Person 4"}`; `START_BALANCE = 10000`
  - `class PaymentError(Exception)`
  - `init_db(path: str) -> None` — create tables if missing; seed accounts if empty
  - `reset_db(path: str) -> None` — delete all payments, set every balance to `START_BALANCE`
  - `get_balance(path, person_id: int) -> int`
  - `send_payment(path, sender: int, recipient: int, amount: int, note: str = "") -> dict` — returns `{"id", "sender", "recipient", "amount", "note", "created_at"}` (created_at ISO string); raises `PaymentError` on invalid input
  - `history(path, person_id: int) -> list[dict]` — payments where person is sender or recipient, newest first

- [ ] **Step 1: Write `requirements.txt`** (`fastapi`, `uvicorn[standard]`, `httpx`, `pytest`), create venv `.venv`, install. Add `.venv/`, `*.db`, `__pycache__/` to `.gitignore`.
- [ ] **Step 2: Write failing tests** in `tests/test_db.py` (fixture `db` = `tmp_path/"t.db"` after `init_db`):
  - `test_starting_balances`: all four `get_balance == 10000`
  - `test_payment_moves_money`: `send_payment(db,1,2,250,"lunch")` → balances 9750 / 10250; returned dict has amount 250, note "lunch"
  - `test_history_newest_first`: two payments 1→2 then 3→1; `history(db,1)` ids in reverse order, length 2; `history(db,4) == []`
  - `test_insufficient_funds`: `send_payment(db,1,2,10001)` raises `PaymentError`; balances unchanged
  - `test_double_spend`: 6000 then 6000 from 1 → second raises; balance 4000
  - `test_invalid`: raises for amount 0, -5, recipient 9, recipient == sender, amount `True`/`2.5`
  - `test_reset`: after a payment, `reset_db` → balances 10000, history empty
- [ ] **Step 3: Run** `.venv/bin/pytest tests/test_db.py -q` — Expected: FAIL (module not found)
- [ ] **Step 4: Implement `server/db.py`.** Tables `accounts(id INTEGER PK, name TEXT, balance INTEGER)` and `payments(id INTEGER PK AUTOINCREMENT, sender, recipient, amount, note, created_at)`. Open a fresh connection per call; `send_payment` validates (`type(amount) is int`), then `BEGIN IMMEDIATE`, check balance, update both, insert, commit.
- [ ] **Step 5: Run** `.venv/bin/pytest tests/test_db.py -q` — Expected: 7 passed
- [ ] **Step 6: Commit** `feat: payments database`

### Task 2: Orchestrator and per-person app

**Files:**
- Create: `server/orchestrator.py`, `server/app.py`, `web/index.html` (stub `<h1>phone</h1>` for now)
- Test: `tests/test_app.py`

**Interfaces:**
- Consumes: Task 1 `server/db.py`.
- Produces:
  - `Orchestrator` with `async connect(person_id: int, ws: WebSocket)`, `disconnect(person_id, ws)`, `async send(person_id: int, event: dict)` (sends JSON to every socket of that person; drops sockets that raise), `async broadcast(event: dict)`
  - `create_app(person_id: int, orch: Orchestrator, db_path: str) -> FastAPI`:
    - `GET /` → `web/index.html`; static files mounted at `/static` from `web/`
    - `GET /api/state` → `{"me": {"id", "name"}, "people": [{"id","name"}...], "balance": int, "history": [...]}`
    - `POST /api/payments` body `{"recipient": int, "amount": int, "note": str?}` → 200 payment dict; 400 `{"detail": msg}` on `PaymentError` or bad body
    - `WS /ws` → registered under this app's person
  - Events over WS (JSON): after a payment, recipient gets `{"type":"payment_received","payment":{...},"from":"Person 1","text":"Person 1 sent you 250 CZK"}`; sender gets `{"type":"payment_sent","payment":{...}}`.

- [ ] **Step 1: Write failing tests** in `tests/test_app.py`. Fixture builds one shared `Orchestrator`, a `tmp_path` DB, and `TestClient(create_app(n, orch, db))` for n=1..4.
  - `test_state`: client1 `/api/state` → me.id 1, balance 10000, 4 people
  - `test_payment_notifies_recipient`: open `client2.websocket_connect("/ws")`; client1 POST `{"recipient":2,"amount":250,"note":"lunch"}` → 200; ws receives `type == "payment_received"` and `text == "Person 1 sent you 250 CZK"`
  - `test_two_tabs_same_person`: two ws on client2, both receive the event
  - `test_bad_amounts`: POST amounts `"250"`, `2.5`, `0`, `-1`, missing → all 400; balance still 10000
  - `test_self_payment_400`: client1 pays recipient 1 → 400
  - `test_dead_socket_skipped` (unit, asyncio): `Orchestrator` with one fake socket whose `send_json` raises and one recording socket for the same person; `await send(...)` → recorder got the event, dead socket removed
  - `test_index_served`: `GET /` → 200, html
- [ ] **Step 2: Run** `.venv/bin/pytest tests/test_app.py -q` — Expected: FAIL (import error)
- [ ] **Step 3: Implement** `server/orchestrator.py` and `server/app.py`. Parse POST body as raw JSON and validate types yourself (so `"250"` is rejected, not coerced).
- [ ] **Step 4: Run** `.venv/bin/pytest -q` — Expected: all passed
- [ ] **Step 5: Commit** `feat: orchestrator and per-person API`

### Task 3: Launcher

**Files:**
- Create: `run.py`, `README.md` (replace: how to install, run, reset; port → person table)

**Interfaces:**
- Consumes: `create_app`, `Orchestrator`, `init_db`, `reset_db`.
- Produces: `python run.py [--reset] [--db bank.db]`. Starts `uvicorn.Server` for ports 3001–3004 on `127.0.0.1` via `asyncio.gather`. `--reset` calls `reset_db` and exits.

- [ ] **Step 1: Implement `run.py`.**
- [ ] **Step 2: Smoke test:** start in background, `curl -s localhost:3001/api/state` and `localhost:3004/api/state`; POST a payment on 3001 to 3 and check 3003 balance is 10250; then `python run.py --reset` and check 10000. Expected: as stated.
- [ ] **Step 3: Commit** `feat: launcher for four phone servers`

### Task 4: Phone shell (frame, status bar, banner, pull-down)

**Files:**
- Create: `web/phone.css`, `web/phone.js`; Modify: `web/index.html`

**Interfaces:**
- Produces (global `window.Phone`):
  - `Phone.notify({title: str, body: str, color?: str})` — shows banner ~4 s (tap dismisses) and prepends to pull-down list
  - `Phone.onEvent(fn)` — `fn(event)` for every WS event
  - `Phone.me` — `{id, name}` once loaded; `Phone.ready: Promise`
  - The app renders into `#app` inside the phone screen.
- Layout per the approved mockups (`.superpowers/brainstorm/.../full-page.html`, `pulldown-v2.html`): phone aspect 9:19.5, height ~92vh, dark gradient page. Status bar: live local time (left), 5 rising bars (right). Pull-down: pointer drag starting in top 40 px of the screen opens a frosted panel following the finger; release past 30% height → open, else snap back; drag up on panel closes. Panel: big time + 5 bars, list of notifications, 3 dashed "notification placeholder" slots when empty. Person colours: 1 `#3b6cff`, 2 `#2bb673`, 3 `#f5a623`, 4 `#e5487a`. WS reconnects every 2 s if dropped.

- [ ] **Step 1: Implement.**
- [ ] **Step 2: Verify in browser:** run server, open 3001 and 3002, screenshot; call `Phone.notify` from console → banner appears and is listed in pull-down. Expected: matches mockups.
- [ ] **Step 3: Commit** `feat: phone shell with banner and pull-down`

### Task 5: Placeholder bank app

**Files:**
- Create: `web/app.js`, `web/app.css`; Modify: `web/index.html` (include them)

**Interfaces:**
- Consumes: `/api/state`, `POST /api/payments`, `window.Phone`.
- Produces: screen in `#app`: greeting with name, balance card (CZK, formatted `10 000 CZK`), send form (recipient select excluding self, amount, note, Send button), error line, history list (`→ Person 2 −250 CZK` / `← Person 3 +100 CZK`, note, time). On `payment_received`: `Phone.notify({title: from, body: text + note line, color})` and refresh state. On `payment_sent`: refresh state (covers other tabs).

- [ ] **Step 1: Implement.**
- [ ] **Step 2: Verify in browser:** 3001 sends 250 to Person 2 → 3002 shows banner "Person 1 sent you 250 CZK", balance 10 250, history entry; pull-down lists it; 3001 shows 9 750. Sending 20 000 shows an error. Expected: as stated.
- [ ] **Step 3: Run** `.venv/bin/pytest -q` — Expected: all passed
- [ ] **Step 4: Commit** `feat: placeholder bank app`
