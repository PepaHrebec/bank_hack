import pytest
from fastapi.testclient import TestClient

from server import db as server_db
from server.app import create_app
from server.db import (
    PaymentError,
    add_expense_from_payment,
    add_expenses_from_payments,
    card_payment,
    create_group,
    init_db,
    recording,
    send_payment,
    start_recording,
    stop_recording,
)
from server.orchestrator import Orchestrator


@pytest.fixture
def db(tmp_path):
    path = str(tmp_path / "t.db")
    init_db(path)
    return path


@pytest.fixture
def clients(tmp_path):
    path = str(tmp_path / "t.db")
    init_db(path)
    orch = Orchestrator()
    return {n: TestClient(create_app(n, orch, path)) for n in (1, 2, 3, 4)}


def _clock(monkeypatch):
    times = iter(f"2026-01-01T10:00:{s:02d}" for s in range(60))
    monkeypatch.setattr(server_db, "_now", lambda: next(times))


def test_collects_only_card_payments_since_start(db, monkeypatch):
    _clock(monkeypatch)
    card_payment(db, 1, 50, "before")
    assert recording(db, 1) is None
    start_recording(db, 1)
    a = card_payment(db, 1, 100, "A")
    send_payment(db, 1, 2, 30)
    b = card_payment(db, 1, 200, "B")
    card_payment(db, 2, 999, "other person")
    rec = recording(db, 1)
    assert [p["id"] for p in rec["payments"]] == [a["id"], b["id"]]
    assert rec["total"] == 300
    assert isinstance(rec["payments"][0], dict)


def test_stop_returns_payments_and_ends(db, monkeypatch):
    _clock(monkeypatch)
    start_recording(db, 1)
    card_payment(db, 1, 100, "A")
    before = recording(db, 1)
    assert stop_recording(db, 1) == before
    assert recording(db, 1) is None
    with pytest.raises(PaymentError, match="Žádná skupinová platba neběží"):
        stop_recording(db, 1)


def test_stop_with_nothing_collected(db):
    start_recording(db, 1)
    out = stop_recording(db, 1)
    assert out["payments"] == [] and out["total"] == 0


def test_start_twice_rejected(db):
    start_recording(db, 1)
    with pytest.raises(PaymentError, match="Skupinová platba už běží"):
        start_recording(db, 1)


def test_create_group_with_sources(db):
    a = card_payment(db, 1, 100, "Pivo")
    b = card_payment(db, 1, 250, "")
    g = create_group(db, 1, "Hospoda", [2], sources=[{"kind": "card", "id": a["id"]}, {"kind": "card", "id": b["id"]}])
    exp = [e for gr in server_db.groups_for(db, 1) if gr["id"] == g["id"] for e in gr["expenses"]]
    assert sorted((e["amount"], e["description"]) for e in exp) == [(100, "Pivo"), (250, "Platba kartou")]
    assert all(e["payer"] == 1 and e["source_kind"] == "card" for e in exp)


def test_batch_skips_payments_already_in_group(db):
    g = create_group(db, 1, "G", [2])
    a = card_payment(db, 1, 100, "A")
    b = card_payment(db, 1, 200, "B")
    add_expense_from_payment(db, g["id"], 1, "card", a["id"])
    out = add_expenses_from_payments(
        db, g["id"], 1, [{"kind": "card", "id": a["id"]}, {"kind": "card", "id": b["id"]}])
    assert [e["source_id"] for e in out["added"]] == [b["id"]]
    assert out["skipped"] == 1


def test_batch_rejects_others_payment(db):
    g = create_group(db, 1, "G", [2])
    mine = card_payment(db, 1, 100, "mine")
    theirs = card_payment(db, 2, 50, "theirs")
    with pytest.raises(PaymentError, match="Platba nebyla nalezena"):
        add_expenses_from_payments(
            db, g["id"], 1, [{"kind": "card", "id": mine["id"]}, {"kind": "card", "id": theirs["id"]}])
    assert all(gr["expenses"] == [] for gr in server_db.groups_for(db, 1))


def test_start_twice_rejected_and_tabs_notified(clients):
    with clients[1].websocket_connect("/ws") as a, clients[1].websocket_connect("/ws") as b:
        r = clients[1].post("/api/recording/start")
        assert r.status_code == 200 and "started_at" in r.json()
        assert a.receive_json() == {"type": "recording_changed"}
        assert b.receive_json() == {"type": "recording_changed"}
        r = clients[1].post("/api/recording/start")
        assert r.status_code == 400
        assert r.json()["detail"] == "Skupinová platba už běží"
    assert clients[1].get("/api/state").json()["recording"]["payments"] == []


def test_card_payment_event_marks_recording(clients, monkeypatch):
    _clock(monkeypatch)  # whole-second timestamps would otherwise put the first card in the recording
    with clients[1].websocket_connect("/ws") as ws:
        clients[1].post("/api/card-payments", json={"amount": 10, "note": "x"})
        assert "recording" not in ws.receive_json()
        clients[1].post("/api/recording/start")
        assert ws.receive_json()["type"] == "recording_changed"
        clients[1].post("/api/card-payments", json={"amount": 20, "note": "y"})
        ev = ws.receive_json()
        assert ev["recording"] is True
        assert ev["text"].endswith(" · přidáno do skupinové platby")
        r = clients[1].post("/api/recording/stop")
        assert r.json()["total"] == 20


def test_http_groups_with_sources(clients):
    c = clients[1].post("/api/card-payments", json={"amount": 70, "note": "A"}).json()
    d = clients[1].post("/api/card-payments", json={"amount": 80, "note": "B"}).json()
    g = clients[1].post("/api/groups", json={"name": "G", "members": [2], "sources": [{"kind": "card", "id": c["id"]}]}).json()
    r = clients[1].post(f"/api/groups/{g['id']}/expenses",
                        json={"sources": [{"kind": "card", "id": c["id"]}, {"kind": "card", "id": d["id"]}]})
    assert r.status_code == 200
    assert r.json()["skipped"] == 1 and len(r.json()["added"]) == 1
