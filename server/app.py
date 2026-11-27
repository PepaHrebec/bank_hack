"""One phone's server: the page, the payments API and the live connection for one person."""

import json
from pathlib import Path

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool

from server import db
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
        raise BadInput("Invalid JSON")
    if not isinstance(body, dict):
        raise BadInput("Expected a JSON object")
    return body


def _note(body):
    note = body.get("note", "")
    if note is None:
        return ""
    if not isinstance(note, str):
        raise BadInput("Note must be text")
    return note


def create_app(person_id: int, orch: Orchestrator, db_path: str) -> FastAPI:
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
            "me": {"id": person_id, "name": db.PEOPLE[person_id]},
            "people": [{"id": i, "name": n} for i, n in db.PEOPLE.items()],
            "balance": db.get_balance(db_path, person_id),
            "history": db.history(db_path, person_id),
            "today_change": db.day_change(db_path, person_id),
            "to_pay": db.open_requests_for(db_path, person_id),
            "requested": db.requests_by(db_path, person_id),
            "groups": db.groups_for(db_path, person_id),
        }

    @app.post("/api/payments")
    async def pay(request: Request):
        try:
            body = await _json_object(request)
            recipient, amount, note = body.get("recipient"), body.get("amount"), _note(body)
            if type(recipient) is not int:
                raise BadInput("Pick a recipient")
            payment = await run_in_threadpool(
                db.send_payment, db_path, person_id, recipient, amount, note
            )
        except (BadInput, db.PaymentError) as e:
            return _bad(str(e))

        sender_name = db.PEOPLE[person_id]
        await orch.send(recipient, {
            "type": "payment_received",
            "payment": payment,
            "from": sender_name,
            "text": f"{sender_name} sent you {amount} CZK",
        })
        await orch.send(person_id, {"type": "payment_sent", "payment": payment})
        return payment

    @app.post("/api/card-payments")
    async def card_pay(request: Request):
        try:
            body = await _json_object(request)
            payment = await run_in_threadpool(
                db.card_payment, db_path, person_id, body.get("amount"), _note(body)
            )
        except (BadInput, db.PaymentError) as e:
            return _bad(str(e))
        text = f"You paid {payment['amount']} CZK" + (f" · {payment['note']}" if payment["note"] else "")
        await orch.send(person_id, {"type": "card_payment", "payment": payment, "text": text})
        return payment

    me = db.PEOPLE[person_id]

    async def announce_request(req, title=None):
        text = f"{me} requests {req['amount']} CZK" + (f" for {title}" if title else "")
        await orch.send(req["payer"], {"type": "request_received", "request": req, "from": me, "text": text})

    @app.post("/api/requests")
    async def request_money(request: Request):
        try:
            body = await _json_object(request)
            payer, amount, note = body.get("payer"), body.get("amount"), _note(body)
            if type(payer) is not int:
                raise BadInput("Pick a contact")
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
                raise BadInput("Title must be text")
            if not isinstance(shares, dict) or not all(k.isdigit() for k in shares):
                raise BadInput("Shares must map person ids to amounts")
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
            "text": f"{me} paid your request: {payment['amount']} CZK",
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
            "text": f"{me} declined your request: {req['amount']} CZK",
        })
        await orch.send(person_id, {"type": "requests_changed"})
        await notify_group(req["group_id"], {person_id, req["requester"]})
        return req

    # ---- Group Settle ----

    async def group_changed(group):
        for p in group["members"]:
            await orch.send(p, {"type": "group_changed", "group_id": group["id"]})

    def group_of(group_id):
        return next(g for g in db.groups_for(db_path, person_id) if g["id"] == group_id)

    @app.post("/api/groups")
    async def create_group(request: Request):
        try:
            body = await _json_object(request)
            expense = body.get("expense")
            if expense is not None and not isinstance(expense, dict):
                raise BadInput("Expense must be an amount and a description")
            group = await run_in_threadpool(
                db.create_group, db_path, person_id, body.get("name"), body.get("members"), expense
            )
        except (BadInput, db.PaymentError) as e:
            return _bad(str(e))
        for p in group["members"]:
            if p != person_id:
                await orch.send(p, {
                    "type": "group_added",
                    "group": group,
                    "from": me,
                    "text": f"{me} added you to {group['name']}",
                })
        await orch.send(person_id, {"type": "group_changed", "group_id": group["id"]})
        return group

    @app.post("/api/groups/{group_id}/expenses")
    async def add_expense(group_id: int, request: Request):
        try:
            body = await _json_object(request)
            if "source" in body:
                # One of my payments picked from history: {"kind": "card" | "transfer", "id": int}
                source = body["source"]
                if not isinstance(source, dict) or type(source.get("id")) is not int:
                    raise BadInput("Pick a payment from your history")
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
                    "text": f"{me} deleted {done['name']}",
                })
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
                "text": f"{payee} requests {req['amount']} CZK for {group['name']}",
            })
        await group_changed(group)
        return group

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
