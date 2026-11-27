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

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python run.py
```

Open each address in its own browser window. On a phone, drag down from the top edge
of the screen to open the notification panel.

## Reset

Every person starts with 10 000 CZK. To wipe all payments and restore that:

```bash
.venv/bin/python run.py --reset
```

## Tests

```bash
.venv/bin/pytest -q
```

## Layout

- `run.py`: starts the four phone servers
- `server/`: orchestrator, per-phone API, SQLite payments (`bank.db`)
- `web/phone.*`: the phone shell (frame, status bar, notifications, pull-down)
- `web/app.*`: the placeholder bank app; replace it with the real one
