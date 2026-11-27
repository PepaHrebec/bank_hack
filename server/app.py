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


def create_app(person_id: int, orch: Orchestrator, db_path: str) -> FastAPI:
    app = FastAPI(title=f"Phone of {db.PEOPLE[person_id]}")
    app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")

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
        }

    @app.post("/api/payments")
    async def pay(request: Request):
        # Validate by hand so "250" or 2.5 are rejected instead of coerced.
        try:
            body = json.loads(await request.body())
        except ValueError:
            return _bad("Invalid JSON")
        if not isinstance(body, dict):
            return _bad("Expected a JSON object")
        recipient, amount, note = body.get("recipient"), body.get("amount"), body.get("note", "")
        if type(recipient) is not int:
            return _bad("Pick a recipient")
        if note is None:
            note = ""
        if not isinstance(note, str):
            return _bad("Note must be text")
        try:
            payment = await run_in_threadpool(
                db.send_payment, db_path, person_id, recipient, amount, note
            )
        except db.PaymentError as e:
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
