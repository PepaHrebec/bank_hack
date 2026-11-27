# Four-phone bank mockup: design

Date: 2026-11-27 · Status: draft, awaiting approval

## Intent

A hackathon demo stage for a future "enhanced bank application". Four people,
each with their own phone, shown as four separate web pages. When one person
does something in the app, the others see it arrive as a phone-style
notification. The real bank app will be designed later; this work builds the
stage and a placeholder app with simple payments so the stage has something
real to show.

The user cares about how the phones look and behave. The backend only has to
make the frontend work.

## Goals

- Ports 3001–3004 each serve one page = one person's phone (Person 1–4).
- Each page shows a single realistic phone (black bezel, notch, home bar),
  centred and scaled to the browser window's height, on a dark background.
  Nothing else on the page.
- An invisible orchestrator relays actions between phones: a click on one
  phone can make a notification appear on another, live, without reloading.
- Notifications: a banner slides down from the top of the receiving phone,
  stays ~4 s, slides away. Tapping it dismisses it. Each notification is also
  added to that phone's pull-down list.
- Pull-down panel: drag down from the top edge of the phone screen to open,
  drag up to close. Contains only: the time at the top, 5 rising signal bars
  next to it, and the notification list (newest first; dashed placeholder
  slots when empty).
- A database holding simple payments (below).

## Non-goals

- No iOS imitation beyond the frame, status bar, the two system pieces
  above and the home screen below: no lock screen, no other working apps.
- No real authentication, no real money, no multi-currency.
- No production hardening.

## Home screen (added 2026-11-27)

- Swiping up from the bottom edge of the app (not while the pull-down panel
  is open) shrinks it into its icon and shows the home screen.
- Home screen: one empty frosted widget, about half the screen tall; a row of
  filler icons (Tinder, YouTube, Grindr) plus George, the icon for our app;
  a dock of filler icons (Safari, WhatsApp, Spotify, Instagram). Filler icons
  do nothing. Icons are the real App Store artwork, saved in `web/icons/`.
- Tapping George (or a notification banner) opens the app again.

## Anti-goals

- The phone must not look like a website in a box. If it doesn't read as a
  phone on a projector, it has failed even if everything works.
- The placeholder app must stay easy to replace with the real bank app later.

## Simple payments (placeholder app)

- Each of the 4 people has one account, starting balance 10 000 CZK.
- A payment: sender, recipient, amount, optional note, timestamp.
- Sending moves money between balances and stores the payment. Refused if
  the sender's balance is insufficient (sender sees an error).
- The recipient's phone gets a notification: "Person 1 sent you 250 CZK".
  The recipient's balance and history update live.
- App screens (updated 2026-11-27):
  - Main: balance card with a history icon (tap opens History), a Contacts
    button, and a large chat window, empty for now; the smart chatbot comes
    later.
  - Contacts: Settle Up and To be paid icons (To be paid will list the
    requests created by Settle Up; neither is implemented yet) above the
    other three people. Tapping a person opens Send money for them (amount, note).
  - History: payments from the database, newest first. The history stays in
    the database for other uses.
- Data persists across restarts (SQLite file). A reset command restores the
  starting state.
- Notifications themselves are not persisted: the pull-down list clears on
  page reload.

## Approaches

1. One Node.js program serving four ports, live connections, SQLite.
2. Five separate programs (four phones + orchestrator): most "truly
   distributed", but five things to keep running on stage.
3. **Python backend serving four ports with live connections and SQLite.**
   **Chosen by the user.**

## Decided how

- Backend: Python, one process, started with one command. The orchestrator
  and the database live in this process; the four ports all talk to it.
- Frontend: plain HTML/CSS/JS, no build step. The same page is served on all
  four ports; the port decides which person it is.
- The phones receive events from the orchestrator over a live connection
  (push, not polling).

## Left to the builder (Claude's calls, correctable)

- Python web framework and server (e.g. FastAPI + uvicorn, WebSockets).
- SQLite via the standard library.
- Exact visual polish of frame, banner and panel, following the approved
  mockups in `.superpowers/brainstorm/`.
- Phone clock shows the real local time.
- Pull-down works with mouse drag and touch; a quick click-and-drag from the
  top ~40 px of the screen is enough.
- Person names: "Person 1" … "Person 4", each with a colour for its
  notification icon.
- Amounts are whole CZK, greater than zero; you can't pay yourself.
- Reset is a command-line flag/script, not a button in the phone.
