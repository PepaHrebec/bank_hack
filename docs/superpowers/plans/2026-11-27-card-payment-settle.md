# Card Payment → Group Settle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Simulated card payments whose notification has a Group Settle button that opens a new group pre-filled with the payment as an expense.

**Architecture:** Backend in `server/db.py` + `server/app.py` (FastAPI, SQLite, existing Orchestrator events). Frontend: shell `web/phone.js`/`phone.css`/`index.html` (notification action + presenter control), app `web/app.js`/`app.css`.

**Tech Stack:** Python 3.14, FastAPI, sqlite3, pytest (`uv run pytest -q`); plain JS/CSS, no build.

**Spec:** `docs/superpowers/specs/2026-11-27-card-payment-settle-design.md`

## Global Constraints

- Amounts are whole CZK > 0, validated with the existing `_check_amount` (bools and floats refused).
- Card payment note: optional, stripped, at most 60 characters.
- Card payment text exactly: `f"You paid {amount} CZK"` plus `f" · {note}"` when the note is non-empty.
- Errors: `PaymentError` → HTTP 400 `{"detail": msg}` (existing `_bad`).
- Reset clears card payments.
- Existing tests must keep passing (`uv run pytest -q`, currently 102).

## Review Focus

1. Card payment with insufficient funds → 400, balance unchanged. (Task 1 test)
2. Card payment amount as string/float/0/negative/missing → 400. (Task 1 test)
3. Group with starting expense where the expense is invalid → 400 and no group created. (Task 1 test)
4. History mixing transfers and card payments stays newest-first. (Task 1 test)
5. Notification action survives into the pull-down list and opens the app. (Task 2 browser check)

---

### Task 1: Card payments and groups with a starting expense (backend)

**Files:** Modify `server/db.py`, `server/app.py`; Test `tests/test_db.py`, `tests/test_app.py`, `tests/test_groups.py`

**Interfaces — Produces:**
- `db.card_payment(path, person: int, amount: int, note: str = "") -> dict` — `{"id","person","amount","note","created_at"}`; raises `PaymentError("Insufficient funds")` like transfers.
- `db.history(path, person)` items now include `"kind": "transfer"` (existing fields unchanged) or `"kind": "card"` (`{"kind","id","person","amount","note","created_at"}`), merged newest first by `created_at` then id.
- `db.create_group(path, creator, name, members, expense=None)` — `expense` is `{"amount", "description"}` or None; added in the same transaction, payer = creator. Invalid expense → `PaymentError`, nothing created.
- `POST /api/card-payments {"amount": int, "note": str?}` → 200 card payment dict; sends the person's own phones `{"type": "card_payment", "payment": {...}, "text": ...}`.
- `POST /api/groups` accepts optional `"expense": {"amount", "description"}` (non-object → 400).

- [ ] Step 1: failing tests:
  - test_db: card payment lowers balance and appears in history as kind "card" newest-first between transfers; insufficient funds raises and leaves balance; invalid amounts (0, -1, 2.5, "5", True) raise; note longer than 60 raises; reset clears card payments.
  - test_groups: `create_group(..., expense={"amount": 480, "description": "Pivnice"})` → group total 480, expense payer = creator; invalid expense (amount 0) raises and `groups_for(creator) == []`.
  - test_app: POST `/api/card-payments {"amount": 480, "note": "Pivnice U Tygra"}` → 200, own websocket receives `card_payment` with text `"You paid 480 CZK · Pivnice U Tygra"`; empty note → text `"You paid 50 CZK"`; bad bodies → 400; POST `/api/groups` with expense → state shows the expense; with `"expense": 5` → 400.
- [ ] Step 2: run `uv run pytest -q` — Expected: new tests FAIL.
- [ ] Step 3: implement (table `card_payments`; refactor the balance check in `_transfer` into a shared debit helper rather than duplicating it).
- [ ] Step 4: run `uv run pytest -q` — Expected: all pass.
- [ ] Step 5: commit `feat: card payments and groups with a starting expense`.

### Task 2: Presenter control, notification action, Group Settle from the notification (frontend)

**Files:** Modify `web/index.html`, `web/phone.css`, `web/phone.js`, `web/app.js`, `web/app.css`

**Interfaces — Consumes:** Task 1 endpoints/events. **Produces:** `Phone.notify({title, body, color, action?: {label, onClick}})`.

- Presenter control: `<aside class="demo-pay">` in `index.html` after `.phone`, fixed bottom-right of the page, outside the phone; title "Card payment (demo)", Amount and Note inputs, Pay button, message line (error red / "Paid" green). Posts to `/api/card-payments`. Small, unobtrusive, dark translucent card.
- Shell: `notify` stores `action`; banner and pull-down item render a button with `action.label`; clicking it calls `action.onClick()`, opens George (`openApp(appEl)`), closes the pull-down and dismisses the banner, and does not trigger the banner's own tap handler twice.
- App: on `card_payment` event → `Phone.notify({title: "George", body: event.text, color: "#3b6cff", action: {label: "Group Settle", onClick: () => openNewGroup(prefill)}})` and reload; `openNewGroup(prefill)` with `prefill = {amount, note}` sets the name to the note (or empty), shows a line "Expense: 480 CZK · paid by you" (hidden without prefill), and `createGroup` sends `expense: {amount, description: note || "Card payment"}` when prefilled. History renders `kind: "card"` rows as "Card · <note>" (or "Card payment") with a card icon/avatar and `−` amount.

- [ ] Step 1: implement.
- [ ] Step 2: browser check on a scratch server (`uv run run.py --db <tmp> --base-port 4000 --host 127.0.0.1`): on 4001 fill the control (480, "Pivnice U Tygra"), Pay → balance 9 520, banner with "Group Settle" button; click it → New group with name "Pivnice U Tygra" and the expense line; tick Jirka and Pepa, Create → group screen total 480 with expense "Pivnice U Tygra"; 4002 gets "added you" banner; pull-down on 4001 lists the card notification with its button; History shows the card row; amount 999999 shows the error in the control; no page errors.
- [ ] Step 3: run `uv run pytest -q` — Expected: all pass.
- [ ] Step 4: commit `feat: card payment demo control with Group Settle from the notification`.
