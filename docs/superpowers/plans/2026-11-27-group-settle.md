# Group Settle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Groups with members and shared expenses; the creator approves, which runs a pluggable split and turns its result into ordinary payment requests.

**Architecture:** New SQLite tables in `server/db.py`; `server/settle.py` holds the split slot (empty for now); FastAPI endpoints in `server/app.py` push `group_*` events through the existing Orchestrator; `web/app.js` gets three new in-app views (groups, newgroup, group).

**Tech Stack:** Python 3.14, FastAPI, sqlite3, pytest; plain JS/CSS.

**Spec:** `docs/superpowers/specs/2026-11-27-group-settle-design.md`

## Global Constraints

- Adding/deleting an expense never changes a balance.
- Only the creator approves; approve allowed any time while `open`; after approve the group is `approved` and read-only.
- Settlement output becomes rows in `requests` (status `open`) linked via `request_groups.settle_group_id`; requests in one request group may have different requesters.
- `settle(members, expenses)` in `server/settle.py` returns `[]` for now.
- Group name required, ≤ 40 chars; expense description required, ≤ 60 chars; amounts whole CZK > 0.
- Errors: `PaymentError` in db → HTTP 400 `{"detail": msg}`.
- Reset clears groups, members, expenses.

## Review Focus

1. Non-member reading, adding to, deleting from, or approving a group → refused. (Task 1/2 tests)
2. Deleting someone else's expense, or any expense after approval → refused. (Task 1 test)
3. Approving twice → refused, no duplicate requests. (Task 1 test)
4. Members list with duplicates / self / unknown ids → refused or normalised. (Task 1 test)
5. Settlement requests with several requesters still show correctly in both To be paid tabs. (Task 1 test with a stubbed settle)

---

### Task 1: Groups, expenses and approval in the DB

**Files:** Create `server/settle.py`; Modify `server/db.py`; Test `tests/test_groups.py`

**Interfaces — Produces (`server/db.py`):**
- `create_group(path, creator: int, name: str, members: list[int]) -> dict` — `{"id","name","creator","status","created_at","members":[ids incl. creator]}`
- `add_expense(path, group_id, payer, amount, description) -> dict` — `{"id","group_id","payer","amount","description","created_at"}`
- `delete_expense(path, group_id, expense_id, person) -> None`
- `approve_group(path, group_id, person, split=settle.settle) -> dict` — group dict + `"requests": [...]`
- `groups_for(path, person) -> list[dict]` — newest first, each `{"id","name","creator","status","created_at","approved_at","members":[ids],"expenses":[...newest first],"total"}`
- `server/settle.py`: `settle(members: list[int], expenses: list[dict]) -> list[tuple[int, int, int]]` (payer, payee, amount); returns `[]`.

- [ ] Step 1: write failing tests (create incl. creator + dedupe; invalid names/members; non-member add refused; expense validation; delete own only, not after approve; approve by creator only, twice refused; approve with stub split `lambda m, e: [(2, 1, 300), (3, 4, 100)]` creates requests visible via `open_requests_for(2)` / `requests_by(4)` with group title; adding expense keeps balances; reset clears groups).
- [ ] Step 2: run `uv run pytest tests/test_groups.py -q` — Expected: FAIL (import error)
- [ ] Step 3: implement tables, functions, `request_groups.settle_group_id` (added with `ALTER TABLE` if missing).
- [ ] Step 4: run `uv run pytest -q` — Expected: all pass
- [ ] Step 5: commit `feat: settle groups, expenses and approval in the database`

### Task 2: Group API and events

**Files:** Modify `server/app.py`; Test `tests/test_app.py`

**Interfaces — Consumes:** Task 1. **Produces:** `POST /api/groups {name, members}`, `POST /api/groups/{id}/expenses {amount, description}`, `DELETE /api/groups/{id}/expenses/{eid}`, `POST /api/groups/{id}/approve`; `/api/state` gains `groups`. Events: new members get `{"type":"group_added","group","from","text":"<creator> added you to <name>"}`; on any change all members get `{"type":"group_changed","group_id"}`; approval also sends each request's payer `request_received` (text `"<payee> requests <n> CZK for <name>"`).

- [ ] Step 1: failing tests (create → member gets group_added; expense → members get group_changed; state lists groups; non-creator approve 400; bad bodies 400).
- [ ] Step 2: run — Expected: FAIL
- [ ] Step 3: implement.
- [ ] Step 4: run `uv run pytest -q` — Expected: all pass
- [ ] Step 5: commit `feat: group settle API`

### Task 3: Group Settle screens

**Files:** Modify `web/app.js`, `web/app.css`

**Interfaces — Consumes:** Task 2 API and events.

Views: `groups` (from Group Settle icon; cards: name, "Created by me"/"Added by <first name>", status pill Open/Approved, total, member avatars; "+ New group"), `newgroup` (name field, tick list of the other three, Create), `group` (header name, members, total, expense list with Delete on own while open, add form amount + what for while open, Approve for creator while open; approved note "Approved: split algorithm not implemented yet" when no requests were created). Notifications for `group_added`; reload on `group_changed`.

- [ ] Step 1: implement.
- [ ] Step 2: browser check on a scratch server (`--base-port 4000`): create group on 4001 adding 2 and 3 → 4002 banner + group listed; 4002 adds expense → 4001 sees it live; 4002 cannot see Approve; 4001 approves → status Approved, add form gone; no page errors.
- [ ] Step 3: `uv run pytest -q` — Expected: all pass
- [ ] Step 4: commit `feat: Group Settle screens`
