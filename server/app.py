"""One phone's server: the page, the payments API and the live connection for one person."""

import asyncio
import json
import logging
from pathlib import Path

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool

from server import accounts, chat, db
from server.banks import BANKS
from server.orchestrator import Orchestrator

WEB_DIR = Path(__file__).resolve().parent.parent / "web"


def _bad(msg):
    return JSONResponse({"detail": msg}, status_code=400)


class BadInput(Exception):
    pass


async def _json_object(request):
    # Validate by hand so "250" or 2.5 are rejected instead of coerced.
    try:
        body = json.loads(await request.body())
    except ValueError:
        raise BadInput("Neplatný JSON")
    if not isinstance(body, dict):
        raise BadInput("Očekává se JSON objekt")
    return body


def _note(body):
    note = body.get("note", "")
    if note is None:
        return ""
    if not isinstance(note, str):
        raise BadInput("Poznámka musí být text")
    return note


CHAT_MAX_MESSAGES = 20
CHAT_MAX_CHARS = 1000


def _chat_messages(body):
    messages = body.get("messages")
    if not isinstance(messages, list) or not 1 <= len(messages) <= CHAT_MAX_MESSAGES:
        raise BadInput(f"Pošli 1 až {CHAT_MAX_MESSAGES} zpráv")
    clean = []
    for m in messages:
        if (not isinstance(m, dict) or m.get("role") not in ("user", "assistant")
                or not isinstance(m.get("content"), str) or not 0 < len(m["content"]) <= CHAT_MAX_CHARS):
            raise BadInput(f"Každá zpráva musí mít text do {CHAT_MAX_CHARS} znaků")
        clean.append({"role": m["role"], "content": m["content"]})
    if clean[-1]["role"] != "user":
        raise BadInput("Poslední zpráva musí být od uživatele")
    return clean


def _default_suggest():
    # Imported lazily so the messages work even before the Geoff hook module exists.
    try:
        from server import geoff_hook
    except ImportError:
        return None
    return geoff_hook.suggest


def create_app(person_id: int, orch: Orchestrator, db_path: str, chat_complete=None, suggest=None) -> FastAPI:
    app = FastAPI(title=f"Phone of {db.PEOPLE[person_id]}")
    app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")

    @app.middleware("http")
    async def no_stale_pages(request: Request, call_next):
        # The demo changes often; a reload must always pick up the newest page and scripts.
        response = await call_next(request)
        if request.url.path == "/" or request.url.path.startswith("/static/"):
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.get("/")
    def index():
        return FileResponse(WEB_DIR / "index.html")

    @app.get("/api/state")
    def state():
        return {
            "me": {"id": person_id, "name": db.PEOPLE[person_id], "account": db.ACCOUNTS[person_id]},
            "people": [{"id": i, "name": n, "account": db.ACCOUNTS[i]} for i, n in db.PEOPLE.items()],
            "friends": db.friends_of(db_path, person_id),
            "contacts": [{"account": a, "name": n} for a, n in db.CONTACTS.items()],
            "balance": db.get_balance(db_path, person_id),
            "history": db.history(db_path, person_id),
            "today_change": db.day_change(db_path, person_id),
            "to_pay": db.open_requests_for(db_path, person_id),
            "requested": db.requests_by(db_path, person_id),
            "groups": db.groups_for(db_path, person_id),
            "group_invites": db.group_invites_for(db_path, person_id),
            "recording": db.recording(db_path, person_id),
            "session_invites": db.session_invites_for(db_path, person_id),
            "chats": db.chats(db_path, person_id),
        }

    @app.get("/api/accounts")
    def other_accounts():
        return {"accounts": accounts.other_accounts(person_id)}

    async def notify_received(payment):
        sender_name = db.PEOPLE[person_id]
        await orch.send(payment["recipient"], {
            "type": "payment_received",
            "payment": payment,
            "from": sender_name,
            "text": f"{sender_name} ti poslal(a) {payment['amount']} Kč",
        })

    @app.post("/api/payments")
    async def pay(request: Request):
        try:
            body = await _json_object(request)
            recipient, amount, note = body.get("recipient"), body.get("amount"), _note(body)
            if type(recipient) is not int:
                raise BadInput("Vyber příjemce")
            payment = await run_in_threadpool(
                db.send_payment, db_path, person_id, recipient, amount, note
            )
        except (BadInput, db.PaymentError) as e:
            return _bad(str(e))

        await notify_received(payment)
        await orch.send(person_id, {"type": "payment_sent", "payment": payment})
        return payment

    @app.post("/api/friends")
    async def add_friend(request: Request):
        try:
            body = await _json_object(request)
            friend = await run_in_threadpool(db.add_friend, db_path, person_id, body.get("account"))
        except (BadInput, db.PaymentError) as e:
            return _bad(str(e))
        await orch.send(friend, {
            "type": "friend_added",
            "from": me,
            "from_id": person_id,
            "text": f"{me} si tě přidává mezi přátele",
        })
        await orch.send(person_id, {"type": "friends_changed"})
        await orch.send(friend, {"type": "friends_changed"})
        return {"friend": {"id": friend, "name": db.PEOPLE[friend], "account": db.ACCOUNTS[friend],
                           "geoff": True}}

    @app.post("/api/card-payments")
    async def card_pay(request: Request):
        try:
            body = await _json_object(request)
            payment = await run_in_threadpool(
                db.card_payment, db_path, person_id, body.get("amount"), _note(body)
            )
        except (BadInput, db.PaymentError) as e:
            return _bad(str(e))
        text = f"Platba kartou {payment['amount']} Kč" + (f" · {payment['note']}" if payment["note"] else "")
        event = {"type": "card_payment", "payment": payment, "text": text}
        if await run_in_threadpool(db.recording, db_path, person_id):
            event["text"] += " · přidáno do skupinové platby"
            event["recording"] = True
        await orch.send(person_id, event)
        return payment

    @app.post("/api/account-payments")
    async def account_pay(request: Request):
        try:
            body = await _json_object(request)
            account = body.get("account")
            if not isinstance(account, str):
                raise BadInput("Neplatné číslo účtu")
            payment = await run_in_threadpool(
                db.account_payment, db_path, person_id, account, body.get("amount"), _note(body)
            )
        except (BadInput, db.PaymentError) as e:
            return _bad(str(e))
        if payment.get("kind") == "transfer":
            await notify_received(payment)
        await orch.send(person_id, {"type": "payment_sent", "payment": payment})
        return payment

    @app.get("/api/banks")
    def banks():
        return BANKS

    @app.post("/api/recording/start")
    async def recording_start(request: Request):
        try:
            raw = await request.body()
            body = await _json_object(request) if raw.strip() else {}
            invite = body.get("invite", [])
            if not isinstance(invite, list):
                raise BadInput("Pozvaní musí být seznam")
            started = await run_in_threadpool(db.start_recording, db_path, person_id, invite)
        except (BadInput, db.PaymentError) as e:
            return _bad(str(e))
        for p in started["invited"]:
            await orch.send(p, {
                "type": "session_invite",
                "starter": person_id,
                "from": me,
                "text": f"{me} tě zve do skupinové platby",
            })
        await orch.send(person_id, {"type": "recording_changed"})
        return started

    @app.post("/api/recording/invites/{starter}/accept")
    async def session_accept(starter: int):
        try:
            result = await run_in_threadpool(db.accept_session_invite, db_path, person_id, starter)
        except db.PaymentError as e:
            return _bad(str(e))
        for p in {starter, person_id}:
            await orch.send(p, {"type": "recording_changed"})
        return result

    @app.post("/api/recording/invites/{starter}/decline")
    async def session_decline(starter: int):
        try:
            result = await run_in_threadpool(db.decline_session_invite, db_path, person_id, starter)
        except db.PaymentError as e:
            return _bad(str(e))
        for p in {starter, person_id}:
            await orch.send(p, {"type": "recording_changed"})
        return result

    @app.post("/api/recording/stop")
    async def recording_stop():
        try:
            before = await run_in_threadpool(db.recording, db_path, person_id)
            result = await run_in_threadpool(db.stop_recording, db_path, person_id)
        except db.PaymentError as e:
            return _bad(str(e))
        invited = before["invited"] if before else []
        for p in {*result["participants"], *invited}:
            await orch.send(p, {"type": "recording_changed"})
        for p in result["participants"]:
            if p != person_id:
                await orch.send(p, {
                    "type": "session_ended",
                    "from": me,
                    "text": f"{me} ukončil(a) skupinovou platbu",
                })
        return result

    @app.post("/api/recording/group")
    async def recording_group(request: Request):
        try:
            body = await _json_object(request)
            group = await run_in_threadpool(db.create_group_from_session, db_path, person_id, body.get("name"))
        except (BadInput, db.PaymentError) as e:
            return _bad(str(e))
        for p in group["members"]:
            if p != person_id:
                await orch.send(p, {
                    "type": "group_added",
                    "group": group,
                    "from": me,
                    "text": f"{me} tě přidal(a) do skupiny {group['name']}",
                })
        await orch.send(person_id, {"type": "group_changed", "group_id": group["id"]})
        return group

    @app.post("/api/recording/discard")
    async def recording_discard():
        await run_in_threadpool(db.discard_session, db_path, person_id)
        return {"ok": True}

    me = db.PEOPLE[person_id]
    background = set()

    async def announce_request(req, title=None):
        text = f"{me} žádá o {req['amount']} Kč" + (f" za {title}" if title else "")
        await orch.send(req["payer"], {"type": "request_received", "request": req, "from": me, "text": text})

    @app.post("/api/requests")
    async def request_money(request: Request):
        try:
            body = await _json_object(request)
            payer, amount, note = body.get("payer"), body.get("amount"), _note(body)
            if type(payer) is not int:
                raise BadInput("Vyber kontakt")
            req = await run_in_threadpool(db.create_request, db_path, person_id, payer, amount, note)
        except (BadInput, db.PaymentError) as e:
            return _bad(str(e))
        await announce_request(req)
        await orch.send(person_id, {"type": "request_sent", "request": req})
        return req

    @app.post("/api/requests/group")
    async def request_group(request: Request):
        # For Group Settle: {"title": str, "shares": {"<person id>": amount, ...}, "note": str}
        try:
            body = await _json_object(request)
            title, shares, note = body.get("title", ""), body.get("shares"), _note(body)
            if not isinstance(title, str):
                raise BadInput("Název musí být text")
            if not isinstance(shares, dict) or not all(k.isdigit() for k in shares):
                raise BadInput("Podíly musí přiřazovat částky osobám")
            group = await run_in_threadpool(
                db.create_group_request, db_path, person_id, title,
                {int(k): v for k, v in shares.items()}, note,
            )
        except (BadInput, db.PaymentError) as e:
            return _bad(str(e))
        for req in group["requests"]:
            await announce_request(req, group["title"])
        await orch.send(person_id, {"type": "request_sent", "group": group})
        return group

    async def notify_group(group_id, skip):
        # Other members' group cards show who has paid; tell them to refresh.
        if group_id is None:
            return
        for p in db.PEOPLE:
            if p not in skip:
                await orch.send(p, {"type": "requests_changed", "group_id": group_id})

    @app.post("/api/requests/{request_id}/pay")
    async def pay_request(request_id: int):
        try:
            payment = await run_in_threadpool(db.pay_request, db_path, request_id, person_id)
        except db.PaymentError as e:
            return _bad(str(e))
        req = await run_in_threadpool(db.get_request, db_path, request_id)
        await orch.send(payment["recipient"], {
            "type": "payment_received",
            "payment": payment,
            "from": me,
            "text": f"{me} zaplatil(a) tvoji žádost: {payment['amount']} Kč",
        })
        await orch.send(person_id, {"type": "payment_sent", "payment": payment})
        await notify_group(req["group_id"], {person_id, payment["recipient"]})
        return payment

    @app.post("/api/requests/{request_id}/decline")
    async def decline_request(request_id: int):
        try:
            req = await run_in_threadpool(db.decline_request, db_path, request_id, person_id)
        except db.PaymentError as e:
            return _bad(str(e))
        await orch.send(req["requester"], {
            "type": "request_declined",
            "request": req,
            "from": me,
            "text": f"{me} odmítl(a) tvoji žádost: {req['amount']} Kč",
        })
        await orch.send(person_id, {"type": "requests_changed"})
        await notify_group(req["group_id"], {person_id, req["requester"]})
        return req

    # ---- Group Settle ----

    async def group_changed(group):
        for p in group["members"]:
            await orch.send(p, {"type": "group_changed", "group_id": group["id"]})

    def accepted_members(creator, group_id):
        # The creator is always a member, so their view of the group lists everyone who joined.
        return next((g["members"] for g in db.groups_for(db_path, creator) if g["id"] == group_id), [])

    def group_of(group_id):
        return next(g for g in db.groups_for(db_path, person_id) if g["id"] == group_id)

    @app.post("/api/groups")
    async def create_group(request: Request):
        try:
            body = await _json_object(request)
            expense = body.get("expense")
            if expense is not None and not isinstance(expense, dict):
                raise BadInput("Výdaj musí mít částku a popis")
            group = await run_in_threadpool(
                db.create_group, db_path, person_id, body.get("name"), body.get("members"), expense,
                body.get("sources"),
            )
        except (BadInput, db.PaymentError) as e:
            return _bad(str(e))
        for p in group["invited"]:
            await orch.send(p, {
                "type": "group_invite",
                "group": group,
                "from": me,
                "text": f"{me} tě zve do skupiny {group['name']}",
            })
        await orch.send(person_id, {"type": "group_changed", "group_id": group["id"]})
        return group

    @app.post("/api/groups/{group_id}/accept")
    async def accept_invite(group_id: int):
        try:
            group = await run_in_threadpool(db.accept_group_invite, db_path, group_id, person_id)
        except db.PaymentError as e:
            return _bad(str(e))
        await group_changed(group)
        return group

    @app.post("/api/groups/{group_id}/decline")
    async def decline_invite(group_id: int):
        try:
            done = await run_in_threadpool(db.decline_group_invite, db_path, group_id, person_id)
        except db.PaymentError as e:
            return _bad(str(e))
        for p in {*await run_in_threadpool(accepted_members, done["creator"], group_id), person_id}:
            await orch.send(p, {"type": "group_changed", "group_id": group_id})
        return done

    @app.post("/api/groups/{group_id}/expenses")
    async def add_expense(group_id: int, request: Request):
        try:
            body = await _json_object(request)
            if "sources" in body:
                # Several of my payments at once (e.g. a finished Group Payment): [{"kind", "id"}, ...]
                expense = await run_in_threadpool(
                    db.add_expenses_from_payments, db_path, group_id, person_id, body["sources"]
                )
            elif "source" in body:
                # One of my payments picked from history: {"kind": "card" | "transfer", "id": int}
                source = body["source"]
                if not isinstance(source, dict) or type(source.get("id")) is not int:
                    raise BadInput("Vyber platbu ze své historie")
                expense = await run_in_threadpool(
                    db.add_expense_from_payment, db_path, group_id, person_id, source.get("kind"), source["id"]
                )
            else:
                expense = await run_in_threadpool(
                    db.add_expense, db_path, group_id, person_id, body.get("amount"), body.get("description")
                )
        except (BadInput, db.PaymentError) as e:
            return _bad(str(e))
        await group_changed(await run_in_threadpool(group_of, group_id))
        return expense

    @app.delete("/api/groups/{group_id}")
    async def delete_group(group_id: int):
        try:
            done = await run_in_threadpool(db.delete_group, db_path, group_id, person_id)
        except db.PaymentError as e:
            return _bad(str(e))
        for p in done["members"]:
            if p != person_id:
                await orch.send(p, {
                    "type": "group_deleted",
                    "group_id": group_id,
                    "from": me,
                    "text": f"{me} smazal(a) skupinu {done['name']}",
                })
        for p in done["invited"]:
            await orch.send(p, {"type": "group_changed", "group_id": group_id})
        await orch.send(person_id, {"type": "group_changed", "group_id": group_id})
        return done

    @app.delete("/api/groups/{group_id}/expenses/{expense_id}")
    async def delete_expense(group_id: int, expense_id: int):
        try:
            await run_in_threadpool(db.delete_expense, db_path, group_id, expense_id, person_id)
        except db.PaymentError as e:
            return _bad(str(e))
        await group_changed(await run_in_threadpool(group_of, group_id))
        return {"ok": True}

    @app.post("/api/groups/{group_id}/approve")
    async def approve_group(group_id: int):
        try:
            group = await run_in_threadpool(db.approve_group, db_path, group_id, person_id)
        except db.PaymentError as e:
            return _bad(str(e))
        for req in group["requests"]:
            payee = db.PEOPLE[req["requester"]]
            await orch.send(req["payer"], {
                "type": "request_received",
                "request": req,
                "from": payee,
                "text": f"{payee} žádá o {req['amount']} Kč za {group['name']}",
            })
        await group_changed(group)
        for p in group["cancelled_invites"]:
            await orch.send(p, {"type": "group_changed", "group_id": group_id})
        return group

    # ---- WhatsApp mock-up ----

    async def suggest_for(message):
        # Runs in the background after delivery; whatever goes wrong here is only logged.
        try:
            fn = suggest or _default_suggest()
            if fn is None:
                return
            suggestion = await fn(message["text"], person_id, message["recipient"])
            if suggestion is not None:
                await orch.send(person_id, {
                    "type": "geoff_suggestion", "message_id": message["id"], "suggestion": suggestion,
                })
        except Exception:
            logging.getLogger(__name__).warning("Geoff suggestion failed", exc_info=True)

    @app.get("/api/messages")
    async def get_messages(request: Request):
        other = request.query_params.get("with", "")
        if not other.isdigit() or int(other) not in db.PEOPLE or int(other) == person_id:
            return _bad("Vyber kontakt")
        return await run_in_threadpool(db.conversation, db_path, person_id, int(other))

    @app.post("/api/messages")
    async def send_message(request: Request):
        try:
            body = await _json_object(request)
            recipient = body.get("recipient")
            if type(recipient) is not int:
                raise BadInput("Vyber kontakt")
            message = await run_in_threadpool(db.send_message, db_path, person_id, recipient, body.get("text"))
        except (BadInput, db.PaymentError) as e:
            return _bad(str(e))
        await orch.send(recipient, {"type": "message", "message": message})
        await orch.send(person_id, {"type": "message", "message": message})
        # Keep a reference so the task is not garbage-collected before it finishes.
        task = asyncio.create_task(suggest_for(message))
        background.add(task)
        task.add_done_callback(background.discard)
        return message

    @app.post("/api/chat")
    async def chat_endpoint(request: Request):
        try:
            body = await _json_object(request)
            messages = _chat_messages(body)
        except BadInput as e:
            return _bad(str(e))
        # Read per request so the key can be set or removed without restarting.
        complete = chat_complete or chat.openrouter_from_env()
        if complete is None:
            return JSONResponse(
                {"detail": "Chat není nastavený (chybí OPENROUTER_API_KEY nebo OPENROUTER_MODEL)."},
                status_code=503,
            )
        charts = []
        try:
            reply = await asyncio.wait_for(
                chat.run(db_path, person_id, messages, complete, charts=charts), chat.DEADLINE
            )
        except (chat.UpstreamError, asyncio.TimeoutError) as e:
            # The client only sees a generic message; the cause must be findable in the server log.
            logging.getLogger(__name__).warning("Chat upstream failure: %s", str(e) or type(e).__name__)
            return JSONResponse({"detail": "Geoff teď neodpovídá, zkus to prosím znovu."}, status_code=502)
        return {"reply": reply, "charts": charts}

    @app.websocket("/ws")
    async def ws(websocket: WebSocket):
        await orch.connect(person_id, websocket)
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            pass
        finally:
            orch.disconnect(person_id, websocket)

    return app
