# Guided demo: design

## Intent

A stripped-down, guided version of Geoff for presenting to one person at a time. A single phone, where
the viewer is **David Vobecký**, walks through the app with tutorial bubbles: at each step exactly one
thing can be tapped, everything else is blocked. After the last step the overlay goes away and the app
is free to use. Every page refresh starts the whole thing over from a clean state.

It shows, in order: the everyday banking everyone knows; that friends are Geoff users you add by their
`…/0800` account; a manual group with an equal split; a group payment started from the home-screen
widget; the AI chat; and finally the vision of AI living in the phone, shown through the Geoff hook in
WhatsApp.

It lives on its own branch, `demo`, based on `main`. New features from `main` come in by rebasing, so
the demo must touch the existing code as little as possible.

## Goals

- One phone, one viewer, one presenter. A refresh resets everything (database and tour).
- The app looks and behaves exactly like the normal version. The only new thing on screen is the tour
  layer (dimming, a highlight and a bubble).
- The four of us (Štěpán Pressl, Jirka Měřínský, Pepa Hřebec, Petr Šafář) are friends David adds, and
  they react on their own, as if someone were holding their phones.
- Real features where they exist: real payments, real groups and split, real recording session, the
  real chat model and the real WhatsApp hook (OpenRouter key from `.env`).

## Non-goals

- Several viewers at once, hosting, or protecting the API key. This runs on a presenter's laptop.
- A new UI. No visual changes to the app itself.
- Changes to friend rules: friends are still Geoff users only (`…/0800`).

## Anti-goals

- Anything that breaks the normal four-phone mode (`uv run run.py`) or its tests.
- A tour that gets stuck. If a bot or the model is slow or fails, the viewer must still be able to
  continue (see "Failure handling").
- Scattering demo code through `app.js` / `db.py` so every rebase conflicts.

## Approaches

- **A. Demo mode in the existing server (chosen).** `run.py --demo` serves one phone for David. Each page
  load resets and seeds the database through a demo-only endpoint; the four teammates are bots inside
  the server; a new `web/tour.js` overlay drives the tour. Real features stay real.
- **B. Fully client-side with a fake backend in the browser.** No server or database to reset, but every
  API call would need a mock and the chat would be canned, which undercuts the AI step. Dropped.
- **C. Fully scripted screens.** Easy to make bulletproof, but nothing works after the tour, and the app
  must be usable afterwards. Dropped.

## Decided

### People and start state

- David Vobecký is a fifth person, id 5, account `5555555555/0800` (the existing `str(id) * 10` rule;
  it differs from Timothy Liška's `5555555555/0100` by bank code). He exists only in demo mode;
  normal mode keeps the four people and ports 3001–3004.
- The teammates keep their ids and accounts: Štěpán `1111111111/0800`, Jirka `2222222222/0800`,
  Pepa `3333333333/0800`, Petr `4444444444/0800`.
- Start state after each reset (David's view): about three months of salaries and card payments (same
  style as `seed.py`, so "last month" in the chat has real numbers), no friends, no friend requests, no
  groups, no requests, no recording. A short WhatsApp history with Jirka so step 6 isn't an empty chat.
  The teammates have just enough balance to pay what the tour asks of them.

### Reset on refresh

- Demo mode adds `POST /api/demo/reset` (registered only with `--demo`). It cancels any pending bot
  actions, wipes the database and seeds the start state.
- In demo mode the page calls it on every load, before the app's first `/api/state`. So refresh = fresh
  database + tour from step 1.
- Demo mode uses its own database file by default (e.g. `demo.db`), so it never wipes the normal `bank.db`.
- `PEOPLE` and `ACCOUNTS` in `db.py` are module globals (`ACCOUNTS` built at import); demo mode must add
  David to both before any app is created.

### Bots

- The four teammates react to what would be pushed to their phones (the orchestrator events
  `friend_request`, `group_invite`, `session_invite`, `request_received`), after a short delay
  (~1–2 s) so it looks like a person tapping:
  - friend request → accept
  - group invite → accept
  - group-payment (session) invite → accept
  - payment request → pay
- They act through the same code paths their phones would use, so David gets exactly the
  notifications and live updates he gets in the normal app.
- Step 2c only: the bots also start something themselves. When the tour reaches 2c it asks the server
  (a demo-only endpoint) to have Pepa send David a payment request, through Pepa's normal request
  path, so David gets the usual `request_received` notification and the request shows in K zaplacení.
- Step 4 only: once Štěpán has joined David's session and David has made his first card payment, the
  Štěpán bot makes one card payment of its own (e.g. „Benzina 1 600 Kč“), so the shared session holds
  payments from both of them.

### The tour

Czech text, the app's tone. Steps advance when the thing has actually happened in the app (state
changed, view opened, popup appeared, request answered), not merely on a click. During a step, only
the highlighted element(s) accept input; everything else on the page, including the home screen, the
notification pull-down and the 💳 demo chip, is blocked unless the step targets it.

| # | Step | What David does |
|---|------|-----------------|
| 0 | Welcome card | „Ahoj Davide…“, one button to start |
| 1 | Basics | sees balance and today's change; opens history and goes back; Zaplatit to an outside account (number and amount shown in the bubble); opens the QR screen and goes back |
| 2 | Friends | Přátelé → Přidat přítele → types Štěpán's `1111111111/0800` (shown in the bubble) → Štěpán accepts. Then a „Přidat zbytek“ shortcut in the bubble sends requests to Jirka, Pepa and Petr at once; they accept |
| 2b | Request money | Přátelé → Jirka → switches Platba to Žádost → 250 Kč „kino“ → Vyžádat; Jirka's bot pays it; David gets the payment notification |
| 2c | A friend requests from David | the tour has Pepa's bot ask David for 320 Kč „pizza“; the request notification arrives; David opens K zaplacení, taps Zaplatit on Pepa's request and confirms; Pepa gets paid |
| 3 | Group, equal split | creates group „Chata“ with all four, the bots join and add their own costs (Jirka 1 450 Kč „jídlo“, Pepa 780 Kč „pití“, Petr 1 120 Kč „benzín“); David adds 4 000 Kč „ubytování“; approves once all four have accepted and added theirs; the equal split (1 470 Kč each) asks each of the four for what they owe; bots pay; David sees the money come in |
| 4 | Group payment from the widget | goes home; taps Spustit skupinovou platbu on the widget; invites only Štěpán; Štěpán accepts; David pays twice with the 💳 chip (prefilled „Lokál 1 240 Kč“, then a second one); Štěpán's bot pays once; David taps Ukončit skupinovou platbu and creates the group from the result. The step ends there, with no approve or settling |
| 5 | AI chat | opens the chat; the bubble asks him to send „Shrň mi minulý měsíc v platbách mezi všechny obchodníky do grafu“ (a pie chart by merchant); waits for the reply |
| 6 | Vision | a card: in the future AI will be built into phones, see every action locally and offer to act on it. Then: home → WhatsApp → chat with Jirka → sends „Dlužíš mi 450 za lístky“ → the Geoff suggestion appears → he accepts it, sending a payment request; Jirka's bot pays it (the general rule) |
| 7 | Done | „Hotovo, teď si to vyzkoušej sám.“ The overlay is removed for good, until the next refresh |

### Prefill and scrolling

Every form the tour asks for is prefilled with the step's values, and the bubble says so
(„Hodnoty předvyplníme za tebe. Zkontroluj je, než odešleš.“). The highlighted element is scrolled
into view automatically.

### Code placement

- Everything demo-specific sits behind `--demo`: new server module(s) for reset/seed/bots, a new
  `web/tour.js` (+ its CSS) that is only loaded in demo mode.
- Changes to existing files are limited to small hooks the tour needs (e.g. the app announcing that
  its state reloaded or which view is open) and making `PEOPLE`/accounts include David in demo mode.

## Failure handling

- If a bot or the model hasn't done its part within a reasonable time, the bubble offers a way on
  („Pokračovat“), so the tour never hangs. In the chat step, an error reply from the model still lets
  the tour continue.
- If David types something different from what the bubble suggests (wrong account, other amount), the
  app's normal validation answers; the tour waits for the right outcome, and for the friend step the
  bubble keeps showing the number to type.

## My calls (for the human partner to check)

- David as a fifth person (id 5) only in demo mode, rather than renaming Štěpán.
- „Přidat zbytek“ shortcut after the first friend, so step 2 doesn't drag.
- Bots accept/pay everything; none of them declines.
- Step 2b uses Jirka (250 Kč „kino“), step 2c uses Pepa (320 Kč „pizza“); both come right after the friends step.
- Step 4 also has one payment from Štěpán, so the shared split is visible.
- A seeded WhatsApp history with Jirka.
- No skip button for the tour; a refresh is the reset.
- Separate `demo.db` file for demo mode.
- Step 4 ends at creating the group from the session (no approve), since step 3 already showed settling.

## Left to the builder

- How the bots are wired (e.g. a demo orchestrator that reacts to events for ids 1–4 and calls the bot's
  own in-process app), the exact delays, and how pending bot tasks are cancelled on reset.
- How the tour blocks input (overlay with a hole, capture-phase listeners, etc.) and how it finds and
  follows the target elements, including popups and the widget.
- Demo port and how `run.py --demo` prints the address.
- The exact Czech wording of the bubbles, the outside account and amount used in step 1, the second
  card payment in step 4, and the seeded history.
- Tests: the reset/seed and bot reactions should be tested like the existing server code; the tour is
  checked by clicking through it in a browser.
