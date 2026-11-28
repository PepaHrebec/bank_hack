# Pay to account, payment confirmation, Interactive/Classic mode — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. Tasks run in parallel in separate git worktrees and are merged into `stepan4` by the controller.

**Goal:** Remove Tinder; add a "Zaplatit" payment to a Czech bank account number; route every "Zaplatit" on a payment request through a confirmation screen; add an Interactive/Classic mode switch, where Classic shows extra accounts (credit card, savings, pension savings) and Interactive keeps the AI chat, which can summarize those accounts.

**Architecture:** FastAPI + SQLite (`server/db.py`, `server/app.py`), chat tools in `server/chat_tools.py`, vanilla JS UI in `web/app.js` / `web/app.css`, shell API `window.Phone` in `web/phone.js`.

**Tech Stack:** FastAPI, SQLite, pytest, vanilla JS.

**Spec:** none written. The user's request (2026-11-28) is the authority:
1. Remove grindr and tinder.
2. Add a button where I can pay someone, just a "Zaplatit" button. It's a mockup where I enter the bank account number in the Czech format.
3. When I get a notification with Pay/Decline, it should lead me to a confirmation screen.
4. Add a button that toggles between Interactive mode (what we have so far) and Classic mode. Classic mode has several other accounts: credit card, pension savings, savings account. Interactive mode doesn't have these. It has just the interactive AI window, which can summarize them.

## Global Constraints
- All user-visible copy is Czech, with no gendered verbs addressed to the user. Amounts go through `czk()` ("1 234 Kč").
- Existing behaviour not named here keeps working: widget, recording/shared session, groups, WhatsApp, Surfers, chat.
- `uv run pytest -q` passes at the end of every task, and `node --check web/app.js` is clean. Commits end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Never touch the user's servers on 3001–3004 or `bank.db`. Use scratch DBs and ports 3700+ for live checks.
- Follow the surrounding code style: the `el()`/`button()`/`header()`/`show()` helpers, comment density and naming.

## Review Focus
1. An account number with a bad checksum, or a prefix/bank code in the wrong format → a Czech error, and no money moves (Task 2).
2. An account payment over the balance → "Nedostatek prostředků"-style error, as for transfers (Task 2).
3. Confirmation screen, request already paid or declined elsewhere → the error is shown on the screen, and Zpět works (Task 3).
4. A mode switch survives a reload, and works when localStorage throws (Task 4).
5. In Interactive mode, the chat answers "kolik mám na spořicím účtu?" from the new tool. Classic mode shows no chat (Task 4).

---

### Task 1: Remove Tinder (Grindr is already gone)
**Files:** `web/index.html`, `web/fillers.js`, `web/fillers.css`, `web/icons/tinder.png` (delete).
- Remove the Tinder icon from the home grid, the `<section id="tinder">`, `buildTinder` and its CSS. Keep Spotify. Update the header comments that mention Tinder.
- Grep for leftover `tinder` (case-insensitive) in `web/`, `server/` and `tests/`: none remain.
- Commit `chore: remove the Tinder mock-up`.

### Task 2: "Zaplatit" — pay to a Czech bank account
**Files:** `server/db.py`, `server/app.py`, `web/app.js`, `web/app.css`, new `tests/test_account_payments.py`.

**Interfaces (produced):**
- Table `account_payments(id, person, account TEXT, amount INTEGER, note TEXT, created_at)`, created with `IF NOT EXISTS` and cleared in `reset_db`.
- `parse_account(text) -> str` in `server/db.py`:
  - Accepts `[prefix-]number/bank`, where the prefix has ≤6 digits, the number 2–10 digits and the bank code exactly 4 digits. Whitespace is stripped.
  - Validates the Czech mod-11 checksum on the prefix and the number. The weights, from the right, are 1,2,4,8,5,10,9,7,3,6, and the weighted sum must be ≡ 0 mod 11.
  - The number must not be all zeros.
  - Returns the normalised form: the prefix without leading zeros, joined with "-" only when non-zero, then `number/bank`, with no leading zeros on the number.
  - Raises `PaymentError("Neplatné číslo účtu")` otherwise.
  - Valid examples: `19-2000145399/0800`, `2000145399/0800`, `000019-2000145399/0800` (→ `19-2000145399/0800`).
  - Invalid examples: `19-2000145398/0800` (checksum), `2000145399/800`, `abc`.
- `account_payment(path, person, account, amount, note="") -> dict` (keys `id, person, account, amount, note, created_at`):
  - same amount/balance validation and error strings as `send_payment`;
  - deducts the balance in one `_transaction`.
- `history()` includes these as `{"kind": "account", ...}`. `day_change` counts them as outgoing; check it already does for non-incoming kinds.
- `POST /api/account-payments {account, amount, note}` → 200 with the dict, 400 with a Czech `detail` on errors (use the existing `_json_object` / `BadInput` / `_bad` helpers), and pushes `payment_sent` to the person's own tabs, like a transfer.
- Do **not** count account payments in group recording or in chat tools (out of scope).

**UI:**
- A **Zaplatit** button on the main view, next to Kontakty and QR kód (the main tiles become three). Every mode shows it.
- It opens a view "Zaplatit" with fields:
  - "Číslo účtu" (placeholder `123456-1234567890/0100`);
  - "Částka (Kč)";
  - "Zpráva pro příjemce (volitelné)".
- A light client-side format hint is fine, but the server decides validity.
- Submit button "Zaplatit". Success shows `Zaplaceno ${czk(amount)} na účet ${account}`, clears the fields and calls `load()`. Errors show the server's `detail`.
- History and widget rows for `kind === "account"`: label `Na účet ${account}` (note under it in history, like transfers), the card-style icon, outgoing amount.

**Tests:**
- `parse_account` with the valid and invalid examples above;
- the payment deducts the balance and appears in history with kind "account";
- insufficient funds → error, and the balance is unchanged;
- endpoint 200 / 400 (bad account, missing amount).

Commit `feat: pay to a Czech bank account number`.

### Task 3: Confirmation screen for paying a request
**Files:** `web/app.js`, `web/app.css`.
- New view `confirm`, header "Potvrzení platby", with back going to the view that was active before. It shows:
  - the payee's avatar and name;
  - the amount (large, through `czk`);
  - the note, if any;
  - for a group share, the group name.
- Two buttons: **Zrušit** (secondary, goes back) and **Potvrdit platbu** → `POST /api/requests/{id}/pay`.
  - On success, the screen shows "Zaplaceno ✓". After ~1 s, or on a tap, it goes to `main` and calls `load()`.
  - On error, the server's `detail` stays on screen.
- `openConfirm(request)` takes a request dict as sent in `request_received` (`id, requester, amount, note, group?`) or as listed in `state.to_pay`.
- **Notification:** for `request_received`, the inline actions become **Odmítnout** (unchanged, immediate) and **Zaplatit**. Zaplatit no longer pays: it opens Geoff on the confirmation screen (`Phone.openApp("app")` then `openConfirm(event.request)`) and resolves the notification with "Otevřeno".
  - Check in `web/phone.js` how an action's return value is shown, and use it without changing phone.js if possible. If phone.js must change, keep the change minimal and backward compatible.
- **K zaplacení list:** the "Zaplatit" button in `requestRow` also opens the confirmation screen instead of paying at once. Odmítnout stays immediate.

Commit `feat: confirm before paying a request`.

### Task 4: Interactive / Classic mode
**Files:** new `server/accounts.py`, `server/app.py`, `server/chat_tools.py`, `server/chat.py` (only the system prompt, if it lists tools), `web/app.js`, `web/app.css`, new `tests/test_accounts.py`.

**Interfaces (produced):**
- `server/accounts.py`: `other_accounts(person_id) -> list[dict]`, deterministic mock data per person (1–4).
  - Each item is `{"kind": "credit"|"savings"|"pension", "name": str, "balance": int, ...}`:
    - credit: `name "Kreditní karta"`, `limit`, `spent` (balance = −spent), and `transactions: [{"note", "amount", "date"}]` (3–5 Czech merchants);
    - savings: `name "Spořicí účet"`, `balance`, `rate` (e.g. 4.1);
    - pension: `name "Penzijní spoření"`, `balance`, `monthly` (own monthly contribution), `state_contribution` (monthly).
  - Values differ per person and are plausible CZK amounts.
- `GET /api/accounts` → `{"accounts": other_accounts(me)}`.
- Chat tool `accounts_overview`, no arguments. It returns `{"accounts": [...], "total": sum of balances}`, with a Czech description saying it covers the credit card, savings account and pension savings. It is registered wherever the other tools are listed, and dispatched in `call()`.

**UI:**
- A mode switch at the top of the main view: segmented **Interaktivní | Klasický**.
  - Persisted in `localStorage` key `geoff-mode`, with every access wrapped in try/catch. The default is Interaktivní.
  - It applies on load.
- **Interaktivní** (default) is the main view exactly as today: balance card, tiles, recording toggle, the chat with Geoff. No account list.
- **Klasický:**
  - The chat is hidden.
  - The balance card stays, labelled "Běžný účet".
  - Under the tiles and recording toggle there is an "Účty" list with one card per `other_accounts` item, fetched once from `/api/accounts`:
    - credit card: spent / limit and a thin bar;
    - savings: balance and "úrok x,x %";
    - pension: balance and "+ x Kč měsíčně".
  - Tapping a credit-card card opens a simple detail view listing its transactions (header "Kreditní karta", back → main).
  - Tapping the others needs no action.
- The widget is unchanged in both modes.
- Add a quick chip "Moje účty" to the chat's existing chips, if chips exist.

**Tests:**
- `other_accounts` returns the three kinds for each of persons 1–4, deterministically;
- the credit balance equals −spent;
- `/api/accounts` returns them;
- `chat_tools.call(..., "accounts_overview", {})` returns accounts plus total;
- the tool appears in the tool list.

Commit `feat: Interactive/Classic mode with extra accounts`.

---

## Parallel-merge notes (controller)
Tasks 2, 3 and 4 all edit `web/app.js` (2: main tiles + a new view; 3: the notification handler, `requestRow` + a new view; 4: main view composition + a new view). Tasks 2 and 4 both add endpoints to `server/app.py`. The controller merges in the order 1, 3, 2, 4 and resolves conflicts by keeping both sides.
