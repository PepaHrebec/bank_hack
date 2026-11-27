# Geoff: Czech UI, Payment Recording, Chatbot and Mock Data — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rename the bank app to Geoff and translate its UI to Czech. Add a Start/Stop Group Payment recorder that turns the card payments collected during an evening into a Group Settle. Add a read-only Czech chatbot (OpenRouter, server-side tool loop). Add a `--seed` command that fills the database with realistic Czech mock data.

**Architecture:** Everything stays in the existing FastAPI + SQLite + vanilla-JS app. Each phone's server (`server/app.py`) gets new endpoints. Storage lives in `server/db.py`. The chatbot is split into the tools (`server/chat_tools.py`: pure functions over the db for one person) and the harness (`server/chat.py`: the OpenRouter tool-calling loop, with the HTTP call injectable so tests never touch the network). Mock data comes from `server/seed.py`, run via `run.py --seed`.

**Tech Stack:** Python 3.12+, FastAPI, SQLite, httpx (moves from dev to runtime deps for OpenRouter), pytest, vanilla JS/CSS.

**Spec:** This document's *Requirements* section. It records the interview of 2026-11-27, and there is no separate spec file.

## Requirements (from the interview)

**Chatbot**
- Read-only: no tool moves money.
- Four abilities: (a) money in/out over a period, (b) what I owe / what I'm owed (open requests), (c) me and one person (transfers + open requests both ways), (d) Group Settle status.
- The harness runs on the Python server. Env `OPENROUTER_API_KEY` and `OPENROUTER_MODEL`, **no default model**: if either is missing, the chat says it isn't configured.
- Always answers in Czech.
- One-tap suggestion chips.
- Remembers the conversation until page reload. The browser keeps the history and sends it with each message, and the server stores nothing.

**Group payment recording**
- A Start Group Payment toggle in **both** the home widget and the app's main screen. While recording, it reads Stop Group Payment.
- Collects **card payments only**, made between Start and Stop.
- Recording state lives on the **server** (it survives reloads).
- On Stop, a popup opens over the phone screen with: **Create Group Settle** (goes to new-group creation with the collected payments pre-attached, where I pick friends); a list of **open groups I'm a member of** (whoever created them), where picking one copies all collected payments into it as my expenses; and a **"Nic nedělat"** (do nothing) button that just closes.

**Rename + language**
- Every visible "George" becomes "Geoff". The icon is replaced with a new simple generated "G" tile, `web/icons/geoff.svg`.
- The whole UI is in Czech. Filler apps (Tinder, Grindr, Spotify) are third-party mock-ups and stay as they are.

**Mock data**
- `run.py --seed` wipes the database and fills it deterministically, with dates relative to now.
- Covers ~90 days. **Every person has ≥ 200 history items.** About **30 %** of them are transfers to or from friends, and the rest are card payments at Czech businesses plus a monthly salary (a new "income" kind).
- Also includes a few open requests and one open group created by someone else that contains Štěpán.

## Global Constraints

- Base: `stepan3` after Task 1, which merges `origin/main` (contains stepan2's equal-split settle, payment dates and the no-cache fix).
- All user-visible copy is Czech, including `PaymentError` messages and notification `text` built in `server/app.py`. Identifiers, comments, docstrings and commit messages stay English.
- Currency is shown as `Kč` with `cs-CZ` grouping: `10 250 Kč`. Today's change reads `+250 Kč dnes` / `−170 Kč dnes` / `±0 Kč dnes`.
- Glossary (use these words consistently): Balance = **Zůstatek**, Contacts = **Kontakty**, QR code = **QR kód**, Payment/Send = **Platba/Poslat**, Request = **Žádost/Vyžádat**, To be paid = **K zaplacení**, Group Settle = **Skupinové vyrovnání**, Start/Stop Group Payment = **Spustit / Ukončit skupinovou platbu**, Create Group Settle = **Vytvořit skupinové vyrovnání**, Don't do anything = **Nic nedělat**, Salary = **Výplata**.
- Avoid gendered past-tense verbs addressed to the user ("zaplatil jsi"). Use neutral forms ("zaplaceno tebou", "tvoje platba").
- No new runtime dependencies besides moving `httpx` into `[project].dependencies`.
- Code style: match the surrounding code (small helpers, short comments explaining *why*, no frameworks in the frontend).
- Every commit message ends with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Run the suite with `uv run pytest -q`. It must be green at the end of every task.

## Review Focus

1. **Stop with zero card payments collected.** The popup says nothing was collected and offers only "Nic nedělat", and no empty group can be created. (Task 6 manual check; Task 5 test `test_stop_with_nothing_collected`.)
2. **A collected payment is already in the chosen group** (added earlier from history). The others are added and the duplicate is skipped, without failing the whole batch. (Task 5 test `test_batch_skips_payments_already_in_group`.)
3. **Start pressed twice** (two tabs of the same phone, or a double tap). The second call gets a Czech error and both tabs re-sync via a `recording_changed` event. (Task 5 test `test_start_twice_rejected_and_tabs_notified`.)
4. **OpenRouter missing, unreachable or erroring.** The chat shows a Czech error bubble within the timeout, never a hang or a raw stack trace. (Task 7 tests `test_chat_not_configured`, `test_chat_upstream_error`.)
5. **Person names typed loosely in chat** ("pepa", "Hrebec" without diacritics, "Petr"). These resolve to the right friend; an unknown name returns a tool error listing the friends instead of guessing. (Task 7 test `test_with_person_name_matching`.)

---

## File Structure

| File | Responsibility |
|---|---|
| `server/db.py` | + `income` table, history kind `"income"`, `add_income`; + `recordings` table and `start_recording` / `recording` / `stop_recording`; `create_group(..., sources=None)`; `add_expenses_from_payments`. Czech error messages. |
| `server/seed.py` (new) | `seed_db`: deterministic Czech mock data. |
| `server/chat_tools.py` (new) | Tool JSON schemas + `call()`. Read-only queries for one person. |
| `server/chat.py` (new) | System prompt, the tool-calling loop `run()`, and the OpenRouter client `openrouter_from_env()`. |
| `server/app.py` | Czech notification texts; `recording` in `/api/state`; `/api/recording/start|stop`; `sources` on group endpoints; `POST /api/chat`. |
| `run.py` | `--seed`. |
| `web/phone.js` | `Phone.popup(nodes) -> close` modal over the screen. |
| `web/app.js` | Czech copy, Geoff name, income rows, recording toggle (widget + main), stop popup flows, chat UI. |
| `web/app.css`, `web/phone.css` | Styles for the toggle, popup and chat. |
| `web/index.html` | `lang="cs"`, Geoff icon/label. |
| `web/icons/geoff.svg` (new) | Simple "G" tile. |
| `tests/test_seed.py`, `tests/test_recording.py`, `tests/test_chat.py` (new) | Tests per feature. Existing tests are updated for the Czech strings. |

**Execution order and parallelism.** Tasks 2–8 edit `web/app.js` and/or `server/db.py`/`server/app.py`, so run them **sequentially** in the order given. Task 2 (translation) goes first so every later task writes Czech copy against Czech tests. The only safe parallel pair is Task 7's `server/chat_tools.py` + `server/chat.py` (new files) alongside Task 6, provided the Task 7 agent leaves `server/app.py` until Task 6 is merged.

---

### Task 1: Bring stepan3 up to date

**Files:** working tree of `stepan3` (uncommitted widget work + re-applied no-cache fix).

- [ ] **Step 1:** Run `uv run pytest -q` on the working tree as it is. Expected: all pass. The no-cache hunk in the working tree is a verbatim copy of commit `4faea5f`, so it merges cleanly with `origin/main`.
- [ ] **Step 2:** Commit the widget work: `git add -A server web tests && git commit -m "feat: home-screen widget with balance and today's change"` (+ attribution line).
- [ ] **Step 3:** Run `git merge origin/main`. Expected conflicts: `web/app.js`, where main added `stamp()` right after `czk` and the widget added `showChange()` at the same spot (keep both), and possibly `server/app.py`/`tests/test_app.py` no-cache hunks (identical, so keep one copy).
- [ ] **Step 4:** `uv run pytest -q`. Expected: all pass, including `tests/test_settle.py`.
- [ ] **Step 5:** Commit the merge.

---

### Task 2: Geoff + Czech UI

**Files:**
- Modify: `web/index.html`, `web/app.js`, `web/phone.js` (shell copy, e.g. empty notification list), `server/app.py`, `server/db.py`
- Create: `web/icons/geoff.svg`; delete `web/icons/george.png`
- Test: `tests/test_app.py`, `tests/test_db.py`, `tests/test_groups.py` (update expected strings)

**Interfaces:** Produces the glossary above in code, plus `czk(n)` returning `"10 250 Kč"`, used by every later task.

- [ ] **Step 1: Update the tests first.** Change every asserted English user-facing string to Czech. For example, `test_payment_notifies_recipient` now expects `ev["text"] == "Štěpán Pressl ti poslal(a) 250 Kč"`, and `pytest.raises(PaymentError, match="Insufficient funds")` becomes `match="Nedostatek prostředků"`. Use these exact strings for the two that tests share most:
  - payment received: `f"{me} ti poslal(a) {amount} Kč"`
  - insufficient funds: `"Nedostatek prostředků"`
  Pick natural Czech for the rest and assert exactly what you implement.
- [ ] **Step 2:** `uv run pytest -q`. Expected: the updated tests FAIL on the English strings.
- [ ] **Step 3: Translate the server.** Translate all 23 `PaymentError` messages in `server/db.py` and the 8 notification `text`s in `server/app.py`, plus defaults like `"Group payment"` → `"Skupinová platba"` and `"Card payment"` → `"Platba kartou"`.
- [ ] **Step 4: Translate the frontend.** Translate every string in `web/app.js` and the shell strings in `web/phone.js`. Set `lang="cs"` in `index.html`, and `czk` → `` `${n.toLocaleString("cs-CZ")} Kč` ``. Notification title `"George"` → `"Geoff"`. Rename the home icon label to Geoff and point it at `/static/icons/geoff.svg`, and do the same for the widget logo.
- [ ] **Step 5: Create `web/icons/geoff.svg`.** A rounded square (`rx` ≈ 22 % of the size), with a blue gradient matching the old George blue (`#3b6cff` → `#2a4fd6`) and a white bold "G" centred. It must look right at 1.8em (widget) and in the icon grid.
- [ ] **Step 6:** `uv run pytest -q`. Expected: PASS.
- [ ] **Step 7: Manual check.** `uv run python run.py --reset && uv run python run.py`, then open `http://localhost:3001`. No English text remains in Geoff (screens, buttons, empty states, errors, notifications, widget), and the icon and name read Geoff.
- [ ] **Step 8:** Commit `feat: rename to Geoff and translate the UI to Czech`.

---

### Task 3: Income kind (salary)

**Files:**
- Modify: `server/db.py` (table, `add_income`, `history`, `day_change`, `reset_db`), `web/app.js` (history row)
- Test: `tests/test_db.py`

**Interfaces:**
- Produces: `db.add_income(path, person: int, amount: int, note: str) -> dict` returning `{"id","person","amount","note","created_at"}`. History items of `"kind": "income"` carry the same fields. `day_change` counts income as positive.

- [ ] **Step 1: Write the failing tests** in `tests/test_db.py`:

```python
def test_income_raises_balance_and_shows_in_history(db):
    i = add_income(db, 1, 42000, "Výplata")
    assert get_balance(db, 1) == 52000
    assert history(db, 1)[0] == {"kind": "income", **i}
    assert day_change(db, 1) == 42000

def test_reset_clears_income(db):
    add_income(db, 1, 100, "Výplata")
    reset_db(db)
    assert history(db, 1) == [] and get_balance(db, 1) == 10000
```

- [ ] **Step 2:** Run `uv run pytest tests/test_db.py -q`. Expected: FAIL (`add_income` not defined).
- [ ] **Step 3:** Implement the table `income (id INTEGER PRIMARY KEY AUTOINCREMENT, person INTEGER NOT NULL, amount INTEGER NOT NULL, note TEXT NOT NULL, created_at TEXT NOT NULL)` in `init_db`, plus `add_income` (validates amount and person, credits the account) and the `history`/`day_change`/`reset_db` changes.
- [ ] **Step 4:** In `web/app.js`, render an income row in history: an arrow-in icon, `note` as the name, a green `+amount` using the existing `.tx-amount.in`.
- [ ] **Step 5:** `uv run pytest -q`. Expected: PASS.
- [ ] **Step 6:** Commit `feat: income payments (salary) in history and today's change`.

---

### Task 4: Czech mock data (`run.py --seed`)

**Files:**
- Create: `server/seed.py`, `tests/test_seed.py`
- Modify: `run.py`

**Interfaces:**
- Consumes: `db.reset_db`, the table layouts from Task 3.
- Produces: `seed.seed_db(path: str, now: datetime | None = None, rng_seed: int = 7) -> dict[int, int]` (person id → history item count).

- [ ] **Step 1: Write the failing tests** in `tests/test_seed.py`, with a fixed `NOW = datetime(2026, 11, 27, 18, 30)`:
  - `test_everyone_has_at_least_200_payments`: `len(history(db, p)) >= 200` for p in 1..4, and the return value matches.
  - `test_about_30_percent_are_friend_transfers`: per person, `0.25 <= transfers / total <= 0.35`.
  - `test_card_notes_are_czech_businesses`: every card item has a non-empty note, and there are ≥ 25 distinct card notes across all people.
  - `test_monthly_salary`: each person has 3 `income` items with note `"Výplata"`.
  - `test_balances_consistent_and_never_negative`: replaying all of a person's items oldest-first from 10 000 never goes below 0 and ends at `get_balance`.
  - `test_nothing_in_the_future_and_some_today`: every `created_at <= NOW.isoformat()`, and each person has ≥ 2 items dated `NOW.date()`.
  - `test_open_requests_and_group`: `open_requests_for` is non-empty for at least 2 people, and `groups_for(db, 1)` contains an open group whose creator is not 1 and which has ≥ 2 expenses.
  - `test_deterministic_and_wipes_first`: seeding twice with the same `now` gives identical `history(db, 1)`, and a payment made before seeding is gone.
- [ ] **Step 2:** `uv run pytest tests/test_seed.py -q`. Expected: FAIL (module missing).
- [ ] **Step 3: Implement `seed_db`.** `reset_db`, then build all events in memory with `random.Random(rng_seed)` over `now - 89 days … now` (times 07:00–23:30, today's capped at `now`). Sort them chronologically and write them in one transaction, tracking balances. If a debit would go negative, drop that event. Then `UPDATE accounts` with the final balances. Content:
  - salary on the 10th of each of the 3 months: 32 000–48 000 Kč, note `"Výplata"`;
  - card payments with notes from a list of ≥ 30 Czech businesses, each with a realistic amount range: Albert, Lidl, Kaufland, Billa, Penny Market, Tesco, Rohlik.cz, Lokál, Pivovarský dům, U Fleků, Bageterie Boulevard, Ugo, Costa Coffee, Café Louvre, Dámejídlo, Wolt, Bolt, Lítačka DPP, České dráhy, RegioJet, Benzina, Shell, Lékárna Dr.Max, dm drogerie, Rossmann, Alza.cz, Datart, Kino Lucerna, Sportisimo, Decathlon, Knihy Dobrovský, Potrefená husa, Manifesto Market…;
  - friend transfers (~30 % of each person's items) with Czech notes such as "pivo", "oběd", "pizza", "lístky na koncert", "benzín", "dárek pro Janu", "Netflix", "nájem – podíl", "kafe", "taxík". Give some an empty note.
  - After the payments: 4 open requests between different pairs (Czech notes), and one open settle group "Chata Krkonoše" created by person 3 with members 1, 3 and 4 and 3 expenses (via `db.create_group` / `db.add_expense`).
- [ ] **Step 4:** In `run.py`, add `--seed` ("fill the database with Czech mock data and exit"). It prints per-person counts.
- [ ] **Step 5:** `uv run pytest -q`. Expected: PASS. Then run `uv run python run.py --seed --db /tmp/seedcheck.db` and confirm the counts print, with every number ≥ 200.
- [ ] **Step 6:** Commit `feat: run.py --seed fills the database with Czech mock data`.

---

### Task 5: Group payment recording — backend

**Files:**
- Modify: `server/db.py`, `server/app.py`
- Create: `tests/test_recording.py`

**Interfaces:**
- Produces (db):
  - `start_recording(path, person) -> {"started_at": str}`. Raises `PaymentError("Skupinová platba už běží")` if one is already running.
  - `recording(path, person) -> None | {"started_at": str, "payments": [card rows, oldest first], "total": int}`. Card payments with `created_at >= started_at`.
  - `stop_recording(path, person) -> {"started_at", "payments", "total"}`. Deletes the row. Raises `PaymentError("Žádná skupinová platba neběží")`.
  - `create_group(path, creator, name, members, expense=None, sources=None)`. `sources` is a list of `{"kind": "card", "id": int}`, each added like `add_expense_from_payment` in the same transaction.
  - `add_expenses_from_payments(path, group_id, payer, sources) -> {"added": [expense dicts], "skipped": int}`. One transaction. Sources already in the group are skipped and other invalid sources raise. Refactor the body of `add_expense_from_payment` into `_expense_from_payment(conn, group_id, payer, kind, payment_id)` and use it in all three places.
- Produces (HTTP):
  - `/api/state` gains `"recording": db.recording(...)`.
  - `POST /api/recording/start` returns `{"started_at"}`, and `POST /api/recording/stop` returns the stop dict. Both send `{"type": "recording_changed"}` to this person.
  - `POST /api/groups` accepts optional `"sources"`.
  - `POST /api/groups/{id}/expenses` accepts `{"sources": [...]}` (alongside the existing `source` / manual forms), calls `add_expenses_from_payments`, then `group_changed`.
  - While a recording is running, the `card_payment` event's `text` gets the suffix `" · přidáno do skupinové platby"` and an extra field `"recording": true`.
- Table: `recordings (person INTEGER PRIMARY KEY, started_at TEXT NOT NULL)`, cleared by `reset_db`.

- [ ] **Step 1: Write the failing tests** in `tests/test_recording.py` (use the `monkeypatch` `_now` iterator pattern from `test_card_payment_lowers_balance_and_shows_in_history`):
  - `test_collects_only_card_payments_since_start`: a card before start, start, card A, a transfer, card B → `recording()["payments"]` ids are `[A, B]` and `total == A+B`.
  - `test_stop_returns_payments_and_ends`: stop returns the same as `recording()` did, then `recording()` is `None` and a second stop raises `"Žádná skupinová platba neběží"`.
  - `test_stop_with_nothing_collected`: start then stop → `payments == []`, `total == 0`.
  - `test_create_group_with_sources`: the group's expenses equal the cards' amounts and notes, `payer == creator`, and `source_kind == "card"`.
  - `test_batch_skips_payments_already_in_group`: add card A via `add_expense_from_payment`, then a batch of `[A, B]` → `added` has B only, `skipped == 1`.
  - `test_batch_rejects_others_payment`: a source that is someone else's card raises and adds nothing.
  - `test_start_twice_rejected_and_tabs_notified` (in `tests/test_app.py` style, with two `websocket_connect` on client 1): the first start → both sockets get `recording_changed`, and the second start → 400 with `"Skupinová platba už běží"`.
  - `test_card_payment_event_marks_recording`: while recording, the `card_payment` event has `recording is True` and the text ends with the suffix.
- [ ] **Step 2:** `uv run pytest tests/test_recording.py -q`. Expected: FAIL.
- [ ] **Step 3:** Implement the db functions, then the endpoints.
- [ ] **Step 4:** `uv run pytest -q`. Expected: PASS.
- [ ] **Step 5:** Commit `feat: record card payments between Start and Stop Group Payment`.

---

### Task 6: Group payment recording — UI

**Files:**
- Modify: `web/phone.js`, `web/phone.css`, `web/app.js`, `web/app.css`

**Interfaces:**
- Consumes: Task 5 HTTP API and `state.recording`.
- Produces: `Phone.popup(nodes: Node[]) -> close()`, a modal sheet over the whole phone screen (home or any app) with a dimmed backdrop. Tapping the backdrop calls `close()`. Document it in the API comment at the top of `phone.js`.

- [ ] **Step 1: Toggle.** Add one toggle button in the widget (under the today pill) and one on Geoff's main screen (a full-width button under the Contacts/QR tiles). Its label is "Spustit skupinovou platbu", or "Ukončit skupinovou platbu" while `state.recording` is set. While recording, both places also show a red pulsing dot and `"Zaznamenáno: N plateb · X Kč"` (Czech plural: 1 platba, 2–4 platby, 5+ plateb). In the widget, the button's click must `stopPropagation()` so it doesn't open Geoff. Refresh on `recording_changed` and on `card_payment`.
- [ ] **Step 2: Stop popup.** Stop calls `POST /api/recording/stop`, then `Phone.popup(...)` with:
  - the title "Skupinová platba ukončena" and the list of collected payments (note, time, amount) with the total;
  - **"Vytvořit skupinové vyrovnání"** (primary) → `Phone.openApp("app")` then `openNewGroup({ sources, payments })`;
  - under "Nebo přidat do skupiny:", one button per open group I'm in (`state.groups` with `status === "open"`) → `POST /api/groups/{id}/expenses {sources}` → `Phone.openApp("app")`, `openGroup(id)`. If it fails (e.g. the group was approved meanwhile), show the error inside the popup and keep it open;
  - **"Nic nedělat"** (secondary) → `close()`.
  With zero payments, show "Během záznamu nebyla žádná platba kartou." and only "Nic nedělat".
- [ ] **Step 3: New group with sources.** Generalise `openNewGroup(prefill)`. `prefill` is now either the old `{amount, note}` (single card-payment notification) or `{sources, payments}`. In the second case, the name defaults to `"Skupinová platba " + date`, the info line reads `"Výdaje: N plateb · X Kč, zaplaceno tebou"`, and `createGroup()` sends `sources` instead of `expense`. While recording, the `card_payment` notification (event has `recording: true`) has no "Skupinové vyrovnání" action.
- [ ] **Step 4: Manual check.** `uv run python run.py --seed && uv run python run.py`. On phone 1:
  1. Start from the widget. The label flips in the widget and in Geoff.
  2. Make two card payments with the demo card panel. The counter shows "2 platby · …" without opening Geoff.
  3. Stop. The popup lists both and shows "Chata Krkonoše" (created by Pepa).
  4. Pick it. Geoff opens on that group with both expenses.
  5. Repeat with Create: pick friends and create. The group has the payments.
  6. Repeat with zero payments. Only "Nic nedělat" appears.
  7. Reload mid-recording. It is still recording.
- [ ] **Step 5:** `uv run pytest -q` (no regressions). Commit `feat: Start/Stop Group Payment in the widget and Geoff`.

---

### Task 7: Chatbot — tools and harness

**Files:**
- Create: `server/chat_tools.py`, `server/chat.py`, `tests/test_chat.py`
- Modify: `server/app.py`, `pyproject.toml` (move `httpx` to `dependencies`; then `uv lock`)

**Interfaces:**
- `chat_tools.TOOLS: list[dict]`, in OpenAI/OpenRouter `{"type": "function", "function": {name, description, parameters}}` form, with Czech descriptions:
  - `money_flow(period)`, where `period ∈ {"today","yesterday","this_week","last_7_days","this_month","last_month","last_30_days"}` (weeks start Monday). Returns `{"from","to","income","card","transfers_in","transfers_out","total_in","total_out","net","count","largest_out": [≤5 items {kind, amount, note, person?, created_at}]}`.
  - `debts()` returns `{"i_owe": [{"person","amount","note","group"}], "i_owe_total", "owed_to_me": [...], "owed_to_me_total"}` from open requests.
  - `with_person(person: str, days: int = 30)` returns `{"person","days","sent","received","transfers": [last ≤10], "i_owe","owes_me"}`, or `{"error": "Neznámý kontakt. Přátelé: …"}`. Matching is case- and diacritics-insensitive against the full, first and last name. The phone's own person is excluded, and more than one match is an error listing the candidates.
  - `my_groups()` returns `[{"name","status","creator","members","total","i_paid","my_share","balance","unpaid": [{"payer","payee","amount"}]}]`, using `settle.shares`. `unpaid` = open requests of that group's settlement.
- `chat_tools.call(db_path, person_id, name, args: dict, today: date) -> dict`. Unknown tool or bad args give `{"error": ...}` and never raise.
- `chat.run(db_path, person_id, messages: list[dict], complete, today: date | None = None) -> str` (async). `complete(messages, tools) -> dict` is an async function returning an assistant message (`{"role":"assistant","content":..., "tool_calls"?: [...]}`). Loop: prepend the system prompt, call `complete`, run every `tool_calls` entry through `chat_tools.call`, and append `{"role":"tool","tool_call_id","content": json}`. Repeat at most 5 rounds, then return `"Na tohle teď nedokážu odpovědět."`.
- `chat.openrouter_from_env() -> complete | None`. Returns `None` unless both `OPENROUTER_API_KEY` and `OPENROUTER_MODEL` are set. Otherwise it gives an async function that POSTs `https://openrouter.ai/api/v1/chat/completions` with `Authorization: Bearer …`, body `{"model", "messages", "tools"}`, httpx timeout 30 s, and returns `choices[0].message`, raising `chat.UpstreamError` on HTTP or shape errors.
- `create_app(person_id, orch, db_path, chat_complete=None)`. `POST /api/chat` takes `{"messages": [{"role": "user"|"assistant", "content": str}]}`: ≤ 20 messages, each ≤ 1000 chars, last one from the user, otherwise 400. It uses `chat_complete or chat.openrouter_from_env()` (read per request), with `None` → 503 `"Chat není nastavený (chybí OPENROUTER_API_KEY nebo OPENROUTER_MODEL)."` and `UpstreamError`/timeout → 502 `"Geoff teď neodpovídá, zkus to prosím znovu."`. Success → `{"reply": str}`.
- System prompt (exact copy, filled per request):

```
Jsi Geoff, asistent v bankovní aplikaci Geoff. Mluvíš s uživatelem {name}. Dnes je {weekday} {d. m. yyyy}.
Přátelé uživatele: {friends}.
Odpovídej vždy česky, stručně (nejvýš pár řádků), částky piš jako „1 234 Kč“.
Čísla ber jen z nástrojů, nic si nevymýšlej. Umíš: shrnout platby za období, říct, kdo komu dluží (otevřené žádosti),
ukázat platby s jedním přítelem a stav skupinových vyrovnání. Peníze posílat ani žádosti platit neumíš.
Na jiné otázky odpověz, že s tím nepomůžeš, a nabídni, co umíš.
```

- [ ] **Step 1: Write the failing tests** in `tests/test_chat.py`. Seed fixed data with the `_now` monkeypatch and use `today = date(2026, 1, 2)`:
  - `test_money_flow_today`: transfers in/out, a card and income on today plus one yesterday → today's totals and `net` exact; `"yesterday"` returns only that one.
  - `test_period_bounds`: `this_week` for Friday 2026-01-02 is `2025-12-29..2026-01-02`; `last_month` is `2025-12-01..2025-12-31`.
  - `test_debts`: one open request each way plus a paid one → only the open ones, with correct totals.
  - `test_with_person_name_matching`: `"pepa"`, `"Hrebec"`, `"PEPA HŘEBEC"` → person 3. `"Karel"` → `error` containing all three friends' first names. The phone owner's own name → `error`.
  - `test_my_groups`: an approved group with one unpaid request → `unpaid` lists it, and `my_share` comes from `settle.shares`.
  - `test_unknown_tool_returns_error`.
  - `test_run_executes_tool_calls`: a fake `complete` that first returns a `tool_calls` for `debts` and then a final text. Assert the reply and that the second call saw a `tool` message containing `owed_to_me_total`.
  - `test_run_stops_after_5_rounds`: a fake that always asks for a tool → the fallback text.
  - `test_chat_endpoint` (TestClient with `chat_complete=fake`) → 200 `{"reply"}`. A bad body (21 messages / last not user) → 400.
  - `test_chat_not_configured`: `monkeypatch.delenv` both vars, no `chat_complete` → 503 with the exact message.
  - `test_chat_upstream_error`: a fake raising `chat.UpstreamError` → 502 with the exact message.
- [ ] **Step 2:** `uv run pytest tests/test_chat.py -q`. Expected: FAIL.
- [ ] **Step 3:** Implement `chat_tools.py`, then `chat.py`, then the endpoint. Move `httpx` and run `uv lock`.
- [ ] **Step 4:** `uv run pytest -q`. Expected: PASS.
- [ ] **Step 5: Live smoke test**, only if the user has exported the env vars. Run `uv run python run.py --seed && uv run python run.py`, then `curl -s localhost:3001/api/chat -H 'content-type: application/json' -d '{"messages":[{"role":"user","content":"Komu a kolik dlužím?"}]}'`. Expected: a Czech reply naming people and Kč amounts that match `/api/state` `to_pay`.
- [ ] **Step 6:** Commit `feat: read-only Czech chatbot over OpenRouter with payment summary tools`.

---

### Task 8: Chatbot — UI

**Files:**
- Modify: `web/app.js` (the empty `section.chat` on the main screen), `web/app.css`

**Interfaces:** Consumes `POST /api/chat` from Task 7.

- [ ] **Step 1: Build the chat in `section.chat`.**
  - A scrolling message list. User bubbles are right-aligned in the person's accent colour and Geoff bubbles are left-aligned and grey. There is an empty-state line, "Zeptej se mě na své platby.".
  - A chip row. Each chip sends its message: **Dnes** → "Shrň mi dnešní platby.", **Tento měsíc** → "Shrň mi platby za tento měsíc.", **Kolik dlužím?** → "Komu a kolik dlužím?", **Kdo dluží mně?** → "Kdo a kolik dluží mně?", **Moje skupiny** → "Jak jsou na tom moje skupiny?".
  - A text input (maxlength 1000) and a send button.
- [ ] **Step 2: Behaviour.**
  - The history is a module-level array of `{role, content}` and is sent as its last 20 entries.
  - While waiting, show a "…" Geoff bubble and disable send and the chips.
  - On a non-2xx response, show `detail` as an error-styled Geoff bubble and leave it out of the history.
  - On a network failure, show "Geoff je nedostupný.".
  - Render plain text only (`textContent`, keeping line breaks via CSS `white-space: pre-wrap`).
  - The chat is built once in `build()`, so `refresh()` must not wipe it.
- [ ] **Step 3: Manual check.** Use seeded data and the env vars set.
  - Tap each chip and get a sensible Czech answer.
  - Ask "a včera?" after **Dnes** and check that it answers about yesterday (memory).
  - Unset the env vars, restart, ask anything, and get the 503 message as an error bubble.
  - A reload clears the chat.
- [ ] **Step 4:** `uv run pytest -q`. Commit `feat: chat with Geoff on the main screen, with quick chips`.
