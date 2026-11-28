# Bank picker, Geoff accounts, Friends, dismissable notifications — Plan

**User's request (2026-11-28):**
1. Be able to remove notifications.
2. Add choosing of the bank after the slash, with 20 banks from the Czech Republic. If the code of the receiver/sender is 0800, the app should tell the user that they can use Geoff.
3. Add the ability to send to an arbitrary account. Person 1 has 1111111111/0800, the second 2222222222/0800, and so on.
4. Rename Contacts to Friends, and add a button "add a Friend" in the new Friends tab. It connects a user by their account number, so the user can then request payments from them.

**Already done by the controller (commit 1b74138):**
- `db.GEOFF_BANK = "0800"`;
- `db.ACCOUNTS = {1: "1111111111/0800", 2: "2222222222/0800", 3: "3333333333/0800", 4: "4444444444/0800"}`;
- `db.person_by_account(text) -> person id | None` (raises `PaymentError("Neplatné číslo účtu")` on invalid input);
- `/api/state` sends `account` on `me` and on every item of `people`.

## Global Constraints
- Czech copy, neutral gender (no "přidal/a"; use forms like "si tě přidává"), amounts via `czk()`.
- `uv run pytest -q` passes; `node --check` clean on changed JS. TDD for backend changes. Commits end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Match the surrounding style. Never touch servers on 3001–3004 or `bank.db`. Scratch DBs and ports 3700+ only.
- Existing behaviour keeps working (widget, recording, groups, WhatsApp, chat + charts, confirm screen).

---

## Agent A — bank picker + paying any account (tasks 2 and 3)
**Owns:** `server/db.py` (the account-payment area only), `server/app.py` (the account-payments endpoint only), the "Zaplatit" view in `web/app.js` (`buildAccountPay` / `openAccountPay`), its CSS, `tests/test_account_payments.py`.

1. **Bank list:** `BANKS` in a new `server/banks.py`, holding 20 real Czech bank codes with short names.
   - 0800 is labelled "Geoff" in this demo.
   - Include at least: 0100 Komerční banka, 0300 ČSOB, 0600 MONETA, 0710 ČNB, 2010 Fio, 2700 UniCredit, 3030 Air Bank, 5500 Raiffeisenbank, 6210 mBank, 0800 Geoff. Fill the rest with currently operating banks' real codes (e.g. 2250 Creditas, 3060 PKO BP, 4000 Max banka, 5800 J&T Banka, 6363 Partners Banka, 2060 Citfin, 2600 Citibank, 7950 Raiffeisen stavební spořitelna, 8030 Volksbank Raiffeisenbank im Stiftland, 2070 TRINITY BANK). No defunct banks.
   - `GET /api/banks` → `[{"code", "name"}]`.
2. **Form:** the account field becomes `[prefix-]number` text input + `/` + a bank `<select>` (code + name, e.g. "0800 – Geoff"). The full account sent to the server stays `prefix-number/code`. Default selection: none ("Vyber banku"). The server still validates.
3. **0800 hint:** when bank 0800 is selected, show a hint under the form.
   - If the number matches a person (`person_by_account`; expose it as `GET /api/accounts/lookup?account=...` → `{"person": id|null}`, or compute it client-side from `state.people[].account`, whichever is simpler and consistent):
     - when that person is me: "To je tvůj vlastní účet";
     - otherwise: "<Name> používá Geoff – peníze dorazí hned."
   - Unknown 0800 number: "Účet je u Geoff – platba proběhne okamžitě."
   - Any other bank: no hint.
4. **Paying a Geoff account moves real money:** in `account_payment`, if the account belongs to another person, do a normal **transfer** to that person (the same as `send_payment`: their balance goes up, they get the `payment_received` event, history shows a transfer) and return the transfer dict with `"kind": "transfer"`. Your own account → `PaymentError("Nelze platit na vlastní účet")`. Unknown 0800 numbers and other banks behave as now (money leaves the app).
   - The endpoint must send the same events `/api/payments` sends when it becomes a transfer.
   - The UI success message: `Posláno ${czk} pro ${name}` for a transfer, as now for external.
5. **"Sender is 0800" (incoming side):** in history, an incoming transfer's meta line shows the sender's account (e.g. "z účtu 2222222222/0800 · Geoff"). Keep it short.
6. **Tests:**
   - paying 3333333333/0800 from person 1 raises person 3's balance and creates a transfer;
   - own account → error;
   - unknown 0800 → account payment;
   - `/api/banks` has 20 unique 4-digit codes including 0800 "Geoff".

## Agent B — Friends + dismissable notifications (tasks 1 and 4)
**Owns:** `web/phone.js`, `web/phone.css`, the contacts / pay screens in `web/app.js` (`build()` contacts section, `openPay`), new friend functions in `server/db.py` (append, don't edit the account-payment area), new endpoints in `server/app.py` (append), the seed, new `tests/test_friends.py`.

1. **Notifications can be removed:**
   - In the pull-down shade, each notification has a small "×" button, and a horizontal swipe also dismisses it. Use pointer events; mouse dragging must work for the desktop demo.
   - A "Smazat vše" button at the top of the shade when there is at least one notification.
   - A banner can be swiped up or away to dismiss it early.
   - Dismissing must not trigger the notification's tap or action.
   - Removing a notification also removes it from any internal list, so it doesn't come back.
2. **Friends:**
   - DB: table `friends(person INTEGER, friend INTEGER, created_at, PRIMARY KEY(person, friend))`, mutual (both rows written).
   - Migration on `init_db`: if the table is newly created, insert all pairs, so existing databases see no change. `reset_db` keeps all pairs.
   - `seed_db` makes everyone friends **except person 4 (Petr)**, who has no friends, so the demo can add him by `4444444444/0800`.
   - `friends_of(path, person) -> [ids]`.
   - `add_friend(path, person, account) -> friend id`, which uses `person_by_account`. Errors: invalid number → as raised; not a Geoff user → "Tento účet nepatří uživateli Geoff"; yourself → "To je tvůj vlastní účet"; already friends → "Už jste přátelé".
   - `POST /api/friends {account}` → `{"friend": {"id", "name", "account"}}`. It sends the new friend `{"type": "friend_added", "from", "text": f"{me} si tě přidává mezi přátele"}` and `friends_changed` to both. `/api/state` gains `"friends": [ids]`.
   - **UI:** rename "Kontakty" → "Přátelé" everywhere (main tile, view header, back-link titles).
   - The Friends view lists only `state.friends`, rebuilt on refresh (today the list is built once in `build()`; make it re-render). Each row shows name + account number under it. Tap → the existing pay/request screen.
   - A button **"Přidat přítele"** opens a small form or `Phone.popup` with an account-number input (placeholder `4444444444/0800`) → `POST /api/friends` → success closes it and shows the new friend.
   - Handle `friend_added` (notification + `load()`) and `friends_changed` (`load()`).
   - An empty list shows "Zatím žádní přátelé – přidej je podle čísla účtu."
   - Other features keep using all people (groups, WhatsApp, chat); only the Friends list is filtered. If `friends` is missing from the state (an old server), show everyone.
3. **Tests:**
   - migration gives all pairs;
   - seed leaves person 4 without friends;
   - add by account works both ways;
   - each error above;
   - endpoint + websocket `friend_added`.

## Merge
Agents A and B run in parallel in separate git worktrees. The controller merges B then A, resolving conflicts by keeping both sides.
