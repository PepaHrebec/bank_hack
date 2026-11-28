# bank_hack

Mockup of a distributed bank app: four phones, one per person, each on its own port.
When one person does something (e.g. sends money), a hidden orchestrator pushes it to
the others, and their phone shows a notification.

| Port | Person         |
|------|----------------|
| 3001 | Štěpán Pressl  |
| 3002 | Jirka Měřínský |
| 3003 | Pepa Hřebec    |
| 3004 | Petr Šafář     |

## Run

Needs [uv](https://docs.astral.sh/uv/).

```bash
uv run run.py
```

It prints one address per person using your machine's network IP as a nip.io name
(e.g. `http://192-168-1-20.nip.io:3001`, which resolves to `192.168.1.20`), so the pages
also open from other devices on the same network. The nip.io name matters: YouTube won't
play the embedded video in the Spotify mock-up on a page opened by bare IP. Opening
`http://localhost:3001` on this machine works too. Use `--host 127.0.0.1` to keep it
local to this machine.

Open each address in its own browser window. On a phone, drag down from the top edge
of the screen to open the notification panel.

## Demo

```bash
uv run run.py --demo
```

One phone for David Vobecký on port 3005, with a guided tour: a bubble shows what to tap next and
everything else is blocked until the tour ends. Štěpán, Jirka, Pepa and Petr are bots that accept
and pay whatever David sends them. Every page load starts over with a fresh database.

Many people can use it at once: each page load gets its own session (a cookie) with its own SQLite
file in `demo-sessions/`. At most 50 sessions run at once (the least recently used one goes first),
sessions idle for 30 minutes are deleted, and each session may ask the chatbot 15 questions and send
30 WhatsApp messages, since both call the model.

## Reset

Every person starts with 10 000 CZK. To wipe all payments and restore that:

```bash
uv run run.py --reset
```

## Tests

```bash
uv run pytest -q
```

## Layout

- `run.py`: starts the four phone servers
- `server/`: orchestrator, per-phone API, SQLite payments (`bank.db`)
- `web/phone.*`: the phone shell (frame, status bar, notifications, pull-down)
- `web/app.*`: the placeholder bank app; replace it with the real one
