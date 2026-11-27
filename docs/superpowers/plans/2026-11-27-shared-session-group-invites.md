# Shared Session + Group Invites — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Members accept group settles before they join. "Spustit skupinovou platbu" invites friends into a shared recording session that ends in one group with everyone's card payments.

**Architecture:** Server-side state in SQLite (`server/db.py`), HTTP and websocket events in `server/app.py`, UI in `web/app.js` / `web/app.css`, following the existing recording and group patterns.

**Tech Stack:** FastAPI, SQLite, pytest, vanilla JS.

**Spec:** `docs/superpowers/specs/2026-11-27-shared-session-group-invites-design.md`

## Global Constraints
- All user-visible copy is Czech, with no gendered verbs addressed to the user. Amounts go through `czk()` ("1 234 Kč").
- Existing behaviour that the spec doesn't change keeps working: the solo recording Stop popup, the split, the chat tools, the WhatsApp popup, the seed.
- `uv run pytest -q` passes at the end of every task. Commits end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Never touch the user's servers on 3001–3004 or `bank.db`.

## Review Focus
1. An invited person tries to add an expense, approve, or open the group by id → "Skupina nebyla nalezena" (no leak). (Task 1)
2. Approving with an invite still open → the split ignores the invited person and the invite disappears. (Task 1)
3. A friend accepts a session invite after the starter already stopped → a Czech error, and nothing starts recording. (Task 2)
4. A participant (not the starter) presses Stop → a Czech error, and the session continues. (Task 2)
5. A friend already in another session or recording is invited → accepting fails cleanly; the invite stays declinable. (Task 2)

---

### Task 1: Group invites — backend

**Files:** `server/db.py`, `server/app.py`, `server/seed.py`, `server/chat_tools.py` (only if it reads membership), and tests in `tests/test_groups.py`, `tests/test_app.py`, plus new `tests/test_invites.py`.

**Interfaces (produced):**
- Migration: `settle_members.status TEXT NOT NULL DEFAULT 'accepted'`, added via `ALTER TABLE` when missing, like the `source_kind` migration.
- `create_group(path, creator, name, members, expense=None, sources=None, accepted=False)`. The creator is 'accepted'. Members are 'invited', or 'accepted' when `accepted=True` (used by the seed and by Task 2).
- `_group_dict`: `"members"` = accepted only (sorted), plus `"invited": [ids]`.
- `_group_row(conn, group_id, person)` requires **accepted** membership, so every existing action rejects invited people with "Skupina nebyla nalezena".
- `groups_for(path, person)`: accepted groups only (unchanged meaning).
- `group_invites_for(path, person) -> [group dicts]`: open groups where person is invited.
- `accept_group_invite(path, group_id, person) -> group dict`.
- `decline_group_invite(path, group_id, person) -> {"id", "name", "creator"}`. Both raise `PaymentError("Pozvánka nebyla nalezena")` if there is no invite.
- `approve_group`: split over accepted members only, then delete remaining invited rows. The returned dict includes `"cancelled_invites": [ids]`.
- `delete_group` also removes invites.
- HTTP:
  - `/api/state` gains `"group_invites"`.
  - `POST /api/groups` keeps its body. The event to each invited member is now `{"type": "group_invite", "group", "from", "text": f"{me} tě zve do skupiny {name}"}` instead of `group_added`.
  - `POST /api/groups/{id}/accept` and `POST /api/groups/{id}/decline` → `group_changed` to all accepted members and the person.
- Seed: "Chata Krkonoše" is created with `accepted=True`.

- [ ] Write failing tests in `tests/test_invites.py`:
  - create → members invited, the creator's `groups_for` shows it with `invited=[...]`, and the invitee's `groups_for` doesn't;
  - accept → in both lists;
  - decline → gone;
  - an invited person's `add_expense`, `approve_group` or `delete_expense` → "Skupina nebyla nalezena";
  - approve with one accepted and one invited → requests only between accepted people, and the invite is removed;
  - accept/decline with no invite → "Pozvánka nebyla nalezena";
  - accept after approval → error;
  - endpoint test: the invitee's websocket gets `group_invite`, and `/accept` makes the creator get `group_changed`.
- [ ] Run them (FAIL). Implement. Update existing tests that assumed instant membership: use `accepted=True` where the test is about something else, and keep `test_create_group_notifies_members`, changed to expect `group_invite`.
- [ ] `uv run pytest -q` passes. Commit `feat: group settle members accept an invite before they join`.

### Task 2: Shared recording session — backend

**Files:** `server/db.py`, `server/app.py`, and new `tests/test_session.py` (plus existing recording tests that need updating).

**Interfaces (produced):**
- Migration: `recordings` gains `session_starter INTEGER` and `ended_at TEXT` (existing rows: starter = person). New table `session_invites(starter INTEGER, person INTEGER, PRIMARY KEY(starter, person))`. `reset_db` clears it.
- `start_recording(path, person, invite=())`:
  - fails if the person already has a recordings row with no `ended_at`;
  - first discards that starter's own ended session, if any;
  - inserts the starter row (`session_starter = person`) and an invite row per invitee (only other known people, unique).
  - Returns `{"started_at", "invited": [ids]}`.
- `accept_session_invite(path, person, starter)`:
  - needs the invite and the starter's session to be running (no `ended_at`), else `PaymentError("Skupinová platba už skončila")`;
  - the person must have no running recording, else `PaymentError("Už jsi v jiné skupinové platbě")`;
  - inserts the person's row (`started_at = _now()`, `session_starter = starter`) and deletes the invite.
- `decline_session_invite(path, person, starter)` deletes the invite, or raises "Pozvánka nebyla nalezena".
- `session_invites_for(path, person) -> [{"starter", "started_at"}]`.
- `recording(path, person) -> None | {"started_at", "payments", "total", "starter", "participants": [ids accepted incl. starter], "invited": [ids]}`.
  - `payments` and `total` are the person's own.
  - Only running (not ended) rows count.
- `stop_recording(path, person)`:
  - a non-starter participant gets `PaymentError("Skupinovou platbu může ukončit jen ten, kdo ji spustil")`;
  - the starter's stop collects every participant's card payments between their `started_at` and now (each payment dict carries `person`), and deletes the invites.
  - If no friend joined, it deletes the row and returns as today (`{"started_at", "payments", "total"}` plus `"participants": [starter]`).
  - If friends joined, it marks all session rows `ended_at = now` and returns `{"started_at", "payments", "total", "participants", "shared": True}`.
- `create_group_from_session(path, starter, name) -> group dict`:
  - needs an ended shared session of that starter, else "Žádná ukončená skupinová platba";
  - calls `create_group(..., members=participants − starter, accepted=True)` and adds each card payment as its owner's expense (reuse `_expense_from_payment(conn, group_id, payer, "card", id)`, so the create and the expense inserts share one transaction);
  - deletes the session rows.
- `discard_session(path, starter)` deletes the ended session's rows (no error if none).
- HTTP:
  - `POST /api/recording/start {invite: [ids]}` (body optional) → `session_invite` event to each invitee `{"type": "session_invite", "starter", "from", "text": f"{me} tě zve do skupinové platby"}` and `recording_changed` to the starter.
  - `POST /api/recording/invites/{starter}/accept|decline` → `recording_changed` to the starter and the person.
  - `POST /api/recording/stop` → `recording_changed` to all participants. Friends also get `{"type": "session_ended", "from", "text": f"{me} ukončil(a) skupinovou platbu"}`.
  - `POST /api/recording/group {name}` → the group, with `group_added` to friends (already accepted) and `group_changed` to the starter.
  - `POST /api/recording/discard`.
  - `/api/state` gains `"session_invites"`.
  - The `card_payment` "recording" flag keeps working for participants.
- [ ] Failing tests in `tests/test_session.py`:
  - start with invites;
  - accept → recording for the friend with participants;
  - friend card payments before accepting are excluded and after are included;
  - the starter stops → shared result with both people's payments and `person`;
  - `create_group_from_session` → the group has both people accepted, with each payer's expenses;
  - discard;
  - all five Review Focus cases 3–5;
  - solo start/stop unchanged;
  - endpoint test for the `session_invite` and `session_ended` events.
- [ ] Implement, update the old recording tests for the new return keys, `uv run pytest -q` passes, and commit `feat: shared group-payment session with friend invites`.

### Task 3: UI — start popup, invites, shared stop

**Files:** `web/app.js`, `web/app.css`.

- **Start:** when not recording, the toggle (widget and main) opens `Phone.popup` titled "Spustit skupinovou platbu" with a checkbox per friend (avatar + name), **Spustit** and **Zrušit**. Spustit → `POST /api/recording/start {invite}`.
- **Running as a participant (not the starter):** the toggle is replaced by the text "Skupinovou platbu vede <first name>". The rec-info shows your own count and total plus "s <names>".
- **Running as the starter:** as today, plus avatars of who joined and "čeká: <names>" for pending invites.
- **Notifications** (in the `Phone.onEvent` handler; inline actions, as in `request_received`):
  - `session_invite`: Přijmout → `/api/recording/invites/{starter}/accept` → "Přidáno ✓"; Odmítnout → `/decline` → "Odmítnuto".
  - `group_invite`: Přijmout → `/api/groups/{id}/accept` → "Přidáno ✓", then `load()`; Odmítnout → `/decline`.
  - `session_ended`: a plain notification + `load()`.
  - `group_invite`, `session_invite` and `session_ended` also call `load()`.
- **Stop popup, shared result:**
  - title, payments grouped or labelled by person name, the total;
  - a name input (default "Skupinová platba " + date);
  - **Vytvořit skupinové vyrovnání** → `POST /api/recording/group {name}` → open that group;
  - **Nic nedělat** → `POST /api/recording/discard`.
  - A solo result keeps the current popup.
- **Group Settle list:** a "Pozvánky" section with a card per `state.group_invites` item (name, creator, Přijmout/Odmítnout). The group detail shows invited members with a "čeká na přijetí" label.
- [ ] Implement. `node --check web/app.js`, and `uv run pytest -q` passes.
- [ ] Headless-Chrome check on scratch servers (port 3600+): phone 1 starts with Pepa invited; phone 3 accepts from the notification; both make card payments (`/api/card-payments`); phone 1 stops → shared popup → create → the group shows both people's expenses on phones 1 and 3. Then a group invite: phone 1 creates a group with Jirka → phone 2 sees the invite in the notification and in the list, and accepts. Screenshots + a check for no JS exceptions.
- [ ] Commit `feat: invite friends when starting a group payment; accept group invites`.
