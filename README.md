# bank_hack

Mockup of a distributed bank app: four phones, one per person, each on its own port.
When one person does something (e.g. sends money), a hidden orchestrator pushes it to
the others, and their phone shows a notification.

| Port | Person   |
|------|----------|
| 3001 | Person 1 |
| 3002 | Person 2 |
| 3003 | Person 3 |
| 3004 | Person 4 |

## Run

Needs [uv](https://docs.astral.sh/uv/).

```bash
uv run run.py
```

It prints one address per person using your machine's network IP (e.g.
`http://192.168.1.20:3001`), so the pages also open from other devices on the same
network. Use `--host 127.0.0.1` to keep it local to this machine.

Open each address in its own browser window. On a phone, drag down from the top edge
of the screen to open the notification panel.

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
