"""Invisible relay: keeps each person's open phone connections and pushes events to them."""

from collections import defaultdict


class Orchestrator:
    def __init__(self):
        self.sockets = defaultdict(list)

    async def connect(self, person_id, ws):
        await ws.accept()
        self.sockets[person_id].append(ws)

    def disconnect(self, person_id, ws):
        if ws in self.sockets[person_id]:
            self.sockets[person_id].remove(ws)

    async def send(self, person_id, event):
        for ws in list(self.sockets[person_id]):
            try:
                await ws.send_json(event)
            except Exception:
                # A closed tab must not stop delivery to the person's other tabs.
                self.disconnect(person_id, ws)

    async def broadcast(self, event):
        for person_id in list(self.sockets):
            await self.send(person_id, event)
