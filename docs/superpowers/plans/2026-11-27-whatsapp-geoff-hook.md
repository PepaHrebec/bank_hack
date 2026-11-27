# WhatsApp mock-up + Geoff message hook — plan for two parallel agents

## Context

The pitch: banking will live inside the apps people already use, with a local AI model reading your messages and offering bank actions through hooks. For the demo, each of the four phones gets a mock **WhatsApp**. Every message I send goes through a **fast lookup**. When it looks like money, my own Geoff (option A: the writer's phone) pops a notification with **Potvrdit / Zamítnout**:
- **Request payment** — "Pepo, dlužíš mi 300 za pivo" → "Vyžádat 300 Kč od Pepy (pivo)?" → Potvrdit sends the request at once. Pepa gets the usual Pay/Decline notification.
- **Group Settle** — "rozpočítáme chatu, 4 500 za všechny" → "Založit skupinové vyrovnání „Chata“ s Pepou?" → Potvrdit creates the group at once. The amount becomes my first expense if there was one.

Decisions so far:
- Only 1:1 chats.
- The fast lookup is an instant local filter, then the OpenRouter model.
- Potvrdit acts immediately.
- The UI is in Czech, like the rest of Geoff.

## Contract shared by both agents (fixed up front, so they can work in parallel)

`server/geoff_hook.py` (owned by Agent B) exposes:

```python
async def suggest(text: str, sender: int, recipient: int, complete=None) -> dict | None
```
- It returns `None` when nothing should pop up. It never raises and always returns within `HOOK_DEADLINE = 5` s.
- Otherwise it returns one of:
  - `{"kind": "request", "payer": recipient, "amount": int, "note": str}`
  - `{"kind": "group", "name": str (≤ 40), "members": [ids other than sender], "amount": int | None, "note": str}`
- `complete` defaults to `chat.openrouter_from_env()`. Tests pass a fake.

**Agent A** calls it after storing a message, in the background so delivery is never delayed. If the result isn't `None`, it sends the writer's phone (all tabs):
```json
{"type": "geoff_suggestion", "message_id": int, "suggestion": {...as above...}}
```
**Agent B** handles that event in `web/app.js`.

`create_app(person_id, orch, db_path, chat_complete=None, suggest=None)`. The new `suggest` keyword lets Agent A's tests inject a fake. The default is `geoff_hook.suggest`, imported lazily so that Agent A's code runs even before Agent B lands.

**File ownership (no overlap):**
- A: `server/db.py`, `server/app.py`, `server/seed.py`, `web/index.html`, new `web/whatsapp.js` and `web/whatsapp.css`, new `tests/test_messages.py`.
- B: new `server/geoff_hook.py` and `tests/test_geoff_hook.py`, plus `web/app.js` and a small change to `server/chat.py`.

---

## Agent A — WhatsApp app

**Server**
- `db.py`:
  - table `messages(id, sender, recipient, text, created_at)`, cleared by `reset_db`;
  - `send_message(path, sender, recipient, text) -> dict`, with Czech errors for empty text, more than 1000 chars, unknown person, or yourself;
  - `conversation(path, me, other, limit=200)`, oldest first;
  - `chats(path, me)` → per friend, the last message, for the chat list.
- `app.py`:
  - `GET /api/messages?with=<id>` and `POST /api/messages {recipient, text}`, using the existing `_json_object` / `BadInput` / `_bad` helpers;
  - `/api/state` gains `"chats"`;
  - on send, push `{"type": "message", "message": {...}}` to the recipient and the sender (other tabs) via `orch.send`, return the message, then start `asyncio.create_task(...)` with `suggest` → `geoff_suggestion` to the sender;
  - exceptions in that task are logged, never raised.
- `seed.py`: a few short Czech conversations per pair. Some contain trigger phrases, so the demo has history.

**Web**
- `index.html`: add `<section id="whatsapp" class="app-window">` and put `data-opens="whatsapp"` on the existing dock icon (`web/icons/whatsapp.png`). Load `whatsapp.js` and `whatsapp.css`.
- `whatsapp.js`: a self-contained IIFE like `fillers.js`. It talks to the shell only through `window.Phone` (`onEvent`, `notify`, `colors`, `initials`, `openApp`).
  - The chat list shows the 3 friends with an avatar, the last message, a time and an unread dot.
  - The chat view has a WhatsApp-style header, green/white bubbles with times, an input and a send button. Enter sends.
  - The text is set with `textContent` only. Live updates come from `message` events.
  - When a message arrives and that chat isn't open, show `Phone.notify({title: sender name, body: text, color})`, and tapping it opens WhatsApp on that chat.
  - On `connected`, refetch.
- `whatsapp.css`: WhatsApp look (green header, beige chat background), working at the phone's size.

**Tests** in `tests/test_messages.py`, following the `clients` fixture pattern in `tests/test_app.py`:
- send and receive over websocket, both directions;
- conversation order;
- the validation errors;
- `chats` in state;
- a fake `suggest` returning a request means the sender gets `geoff_suggestion` and the recipient doesn't;
- a fake returning `None` sends no suggestion;
- a fake that raises still delivers the message, with no 500.

---

## Agent B — fast model lookup + Geoff popup

**`server/geoff_hook.py`**
1. **`prefilter(text) -> bool`** — instant and local, no network.
   - Fold the text: diacritics stripped, lower-case. Reuse the folding approach of `_fold` in `server/chat_tools.py`, or import it.
   - Return True only for money-ish messages: a number or amount word (`kč`, `korun`, `stovk`, `litr`, `pětku`…), or debt/split words (`dluž`, `vrať`, `pošli mi`, `zaplatil`, `za tebe`, `napůl`, `rozpočít`, `rozděl`, `skupin`, `složíme`…).
   - "ahoj", "jdeme na pivo?" and "v 8 u kina" must return False.
   - A unit test pins this with ~15 positive and negative Czech examples.
2. **`suggest(...)`**
   - If the prefilter says no, return None at once and make no call.
   - Otherwise make one model call with a short Czech classification prompt that asks for **JSON only**: `{"action": "none"|"request"|"group", "amount": int|null, "note": str, "name": str|null, "others": [names]}`, with the chat partner's and the friends' names in the prompt.
   - Parse leniently: take the first `{…}`; a bad parse means None.
   - Validate:
     - a request needs a whole amount > 0;
     - a group's members are the recipient plus any named friends, resolved by reusing `_find_friend`-style matching from `chat_tools`, excluding the sender;
     - the default group name is `"Skupinová platba"`.
   - Wrap in `asyncio.wait_for(…, HOOK_DEADLINE)`. Any `chat.UpstreamError`, timeout or missing config logs a warning and returns None.
3. `chat.py`: drop the `"tools"` key from the request body when the list is empty, so a no-tools classification call is valid. Thinking stays off, as it is now.

**`web/app.js`** — in the `Phone.onEvent` handler, on `geoff_suggestion`, call `Phone.notify({title: "Geoff", body, color: "#3b6cff", actions: [...]})`.
- The body is Czech: "Vyžádat 300 Kč od Pepy Hřebce (pivo)?" or "Založit skupinové vyrovnání „Chata“ s Pepou a Jirkou?" (plus " · 4 500 Kč" when there's an amount).
- Actions: `Zamítnout` (secondary, resolves "Zamítnuto") and `Potvrdit`.
- Potvrdit uses the existing endpoints:
  - request: `POST /api/requests {payer, amount, note}` → "Vyžádáno ✓";
  - group: `POST /api/groups {name, members, expense?: {amount, description: note || name}}` → "Skupina založena ✓".
- Then `load()`. Errors show inline through the existing `actions` error path in `phone.js`.

**Tests** in `tests/test_geoff_hook.py`, never touching the network:
- prefilter examples;
- suggest with a fake `complete`:
  - a request is extracted;
  - a group with a named friend resolves the members;
  - "none" gives None;
  - malformed JSON gives None;
  - an amount of 0 or a string amount gives None;
  - the fake is never called when the prefilter fails;
  - a slow fake hits the deadline and gives None;
  - `complete=None` with no env gives None.
- A MockTransport test that the body has no `tools` key when the list is empty.

---

## Execution

- Save this as `docs/superpowers/plans/2026-11-27-whatsapp-geoff-hook.md` on branch `stepan3`.
- Dispatch **Agent A and Agent B at the same time**. Each gets only its own section plus the Contract section, the Czech/neutral-gender copy rule, the reminder not to touch the user's servers on 3001–3004 or `bank.db`, and the commit trailer `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Because they edit disjoint files, both commit straight to `stepan3`, with `git pull`-free sequential commits. Agent B commits only its own files with `git add <paths>`.
- After both finish: one review of each diff, then one integration check (below).

## Verification

1. `uv run pytest -q` passes, with the existing 581 tests plus both new test files.
2. Prefilter speed: a micro-benchmark of 10 000 messages, under 1 ms each.
3. Live check with `.env` set:
   - `uv run python run.py --seed --db <scratch>`, then serve on ports 3100+.
   - In headless Chrome (CDP) on phone 1, open WhatsApp → Pepa and send "Pepo, dlužíš mi 300 za pivo". A Geoff notification appears within ~2 s. Potvrdit → phone 3 gets the request with Pay/Decline.
   - Send "ahoj, jdeme večer?". No model call is made (check the server log/counter) and no popup appears.
   - Send "rozpočítáme chatu s Jirkou, dal jsem 4 500". Group suggestion → Potvrdit → the group exists for phones 1, 2 and 3 with a 4 500 Kč expense.
   - Screenshots of the chat, the popup and the result.
