import pytest
from fastapi.testclient import TestClient

from server import db as server_db
from server.app import create_app
from server.db import (
    PaymentError,
    accept_session_invite,
    card_payment,
    create_group,
    create_group_from_session,
    decline_session_invite,
    discard_session,
    groups_for,
    init_db,
    recording,
    session_invites_for,
    start_recording,
    stop_recording,
)
from server.orchestrator import Orchestrator


@pytest.fixture
def db(tmp_path, monkeypatch):
    path = str(tmp_path / "t.db")
    init_db(path)
    times = iter(f"2026-01-01T10:00:{s:02d}" for s in range(60))
    monkeypatch.setattr(server_db, "_now", lambda: next(times))
    return path


@pytest.fixture
def clients(tmp_path, monkeypatch):
    path = str(tmp_path / "t.db")
    init_db(path)
    times = iter(f"2026-01-01T10:00:{s:02d}" for s in range(60))
    monkeypatch.setattr(server_db, "_now", lambda: next(times))
    orch = Orchestrator()
    return {n: TestClient(create_app(n, orch, path)) for n in (1, 2, 3, 4)}


def test_start_with_invites(db):
    out = start_recording(db, 1, invite=[2, 3, 2, 1, 99])
    assert out["invited"] == [2, 3]
    assert [i["starter"] for i in session_invites_for(db, 2)] == [1]
    assert session_invites_for(db, 4) == []
    rec = recording(db, 1)
    assert rec["starter"] == 1 and rec["participants"] == [1] and rec["invited"] == [2, 3]
    assert recording(db, 2) is None


def test_accept_gives_friend_a_recording(db):
    start_recording(db, 1, invite=[2])
    accept_session_invite(db, 2, 1)
    assert session_invites_for(db, 2) == []
    rec = recording(db, 2)
    assert rec["starter"] == 1 and rec["participants"] == [1, 2] and rec["invited"] == []
    assert recording(db, 1)["participants"] == [1, 2]


def test_payments_before_accepting_excluded(db):
    start_recording(db, 1, invite=[2])
    before = card_payment(db, 2, 50, "before")
    accept_session_invite(db, 2, 1)
    after = card_payment(db, 2, 70, "after")
    rec = recording(db, 2)
    assert [p["id"] for p in rec["payments"]] == [after["id"]] and rec["total"] == 70
    assert before["id"] not in [p["id"] for p in rec["payments"]]


def test_starter_stop_collects_everyone(db):
    start_recording(db, 1, invite=[2, 3])
    accept_session_invite(db, 2, 1)
    a = card_payment(db, 1, 100, "A")
    b = card_payment(db, 2, 200, "B")
    out = stop_recording(db, 1)
    assert out["shared"] is True and out["participants"] == [1, 2]
    assert [(p["id"], p["person"]) for p in out["payments"]] == [(a["id"], 1), (b["id"], 2)]
    assert out["total"] == 300
    assert session_invites_for(db, 3) == []
    assert recording(db, 1) is None and recording(db, 2) is None


def test_solo_stop_unchanged(db):
    start_recording(db, 1, invite=[2])
    a = card_payment(db, 1, 100, "A")
    out = stop_recording(db, 1)
    assert "shared" not in out and out["participants"] == [1]
    assert [p["id"] for p in out["payments"]] == [a["id"]] and out["total"] == 100
    assert session_invites_for(db, 2) == []
    start_recording(db, 1)  # row gone, can start again


def test_create_group_from_session(db):
    start_recording(db, 1, invite=[2])
    accept_session_invite(db, 2, 1)
    a = card_payment(db, 1, 100, "Pivo")
    b = card_payment(db, 2, 200, "Jídlo")
    stop_recording(db, 1)
    g = create_group_from_session(db, 1, "Hospoda")
    assert g["members"] == [1, 2] and g["invited"] == []
    assert sorted((e["payer"], e["amount"]) for e in g["expenses"]) == [(1, 100), (2, 200)]
    assert groups_for(db, 2)[0]["id"] == g["id"]
    with pytest.raises(PaymentError, match="Žádná ukončená skupinová platba"):
        create_group_from_session(db, 1, "Znovu")
    start_recording(db, 2)  # the friend is free again
    assert a["id"] and b["id"]


def test_create_group_needs_ended_shared_session(db):
    with pytest.raises(PaymentError, match="Žádná ukončená skupinová platba"):
        create_group_from_session(db, 1, "X")
    start_recording(db, 1, invite=[2])
    with pytest.raises(PaymentError, match="Žádná ukončená skupinová platba"):
        create_group_from_session(db, 1, "X")


def test_discard(db):
    start_recording(db, 1, invite=[2])
    accept_session_invite(db, 2, 1)
    stop_recording(db, 1)
    discard_session(db, 1)
    discard_session(db, 1)  # no error when none
    start_recording(db, 2)
    start_recording(db, 1)
    assert groups_for(db, 1) == []


def test_start_discards_own_ended_session(db):
    start_recording(db, 1, invite=[2])
    accept_session_invite(db, 2, 1)
    stop_recording(db, 1)
    start_recording(db, 1)
    assert recording(db, 1)["participants"] == [1]


def test_decline(db):
    start_recording(db, 1, invite=[2])
    decline_session_invite(db, 2, 1)
    assert session_invites_for(db, 2) == []
    assert recording(db, 1)["invited"] == []
    with pytest.raises(PaymentError, match="Pozvánka nebyla nalezena"):
        decline_session_invite(db, 2, 1)


# Review Focus 3
def test_accept_after_starter_stopped(db):
    start_recording(db, 1, invite=[2])
    stop_recording(db, 1)
    with pytest.raises(PaymentError, match="Skupinová platba už skončila"):
        accept_session_invite(db, 2, 1)
    assert recording(db, 2) is None


def test_accept_after_shared_stop_by_other_friend(db):
    start_recording(db, 1, invite=[2, 3])
    accept_session_invite(db, 2, 1)
    stop_recording(db, 1)
    with pytest.raises(PaymentError, match="Skupinová platba už skončila"):
        accept_session_invite(db, 3, 1)
    assert recording(db, 3) is None


# Review Focus 4
def test_participant_cannot_stop(db):
    start_recording(db, 1, invite=[2])
    accept_session_invite(db, 2, 1)
    with pytest.raises(PaymentError, match="Skupinovou platbu může ukončit jen ten, kdo ji spustil"):
        stop_recording(db, 2)
    assert recording(db, 1)["participants"] == [1, 2]
    assert recording(db, 2) is not None


# Review Focus 5
def test_accept_while_in_other_session_fails_but_declinable(db):
    start_recording(db, 1, invite=[3])
    start_recording(db, 2, invite=[3])
    accept_session_invite(db, 3, 2)
    with pytest.raises(PaymentError, match="Už jsi v jiné skupinové platbě"):
        accept_session_invite(db, 3, 1)
    assert [i["starter"] for i in session_invites_for(db, 3)] == [1]
    decline_session_invite(db, 3, 1)
    assert recording(db, 3)["starter"] == 2


def test_accept_while_own_recording_fails_but_declinable(db):
    start_recording(db, 1, invite=[2])
    start_recording(db, 2)
    with pytest.raises(PaymentError, match="Už jsi v jiné skupinové platbě"):
        accept_session_invite(db, 2, 1)
    assert len(session_invites_for(db, 2)) == 1
    decline_session_invite(db, 2, 1)
    assert recording(db, 2)["starter"] == 2


def test_accept_without_invite(db):
    start_recording(db, 1)
    with pytest.raises(PaymentError, match="Skupinová platba už skončila"):
        accept_session_invite(db, 2, 1)


def test_invited_start_blocked_while_running(db):
    start_recording(db, 1)
    with pytest.raises(PaymentError, match="Skupinová platba už běží"):
        start_recording(db, 1, invite=[2])


def test_old_group_invites_untouched(db):
    g = create_group(db, 1, "G", [2])
    assert g["invited"] == [2]


def test_http_session_events(clients):
    with clients[1].websocket_connect("/ws") as w1, clients[2].websocket_connect("/ws") as w2:
        r = clients[1].post("/api/recording/start", json={"invite": [2]})
        assert r.status_code == 200 and r.json()["invited"] == [2]
        ev = w2.receive_json()
        assert ev == {"type": "session_invite", "starter": 1, "from": "Štěpán Pressl",
                      "text": "Štěpán Pressl tě zve do skupinové platby"}
        assert w1.receive_json() == {"type": "recording_changed"}
        assert clients[2].get("/api/state").json()["session_invites"][0]["starter"] == 1
        assert clients[2].post("/api/recording/invites/1/accept").status_code == 200
        assert w1.receive_json() == {"type": "recording_changed"}
        assert w2.receive_json() == {"type": "recording_changed"}
        clients[2].post("/api/card-payments", json={"amount": 40, "note": "x"})
        assert w2.receive_json()["recording"] is True
        r = clients[2].post("/api/recording/stop")
        assert r.status_code == 400
        r = clients[1].post("/api/recording/stop")
        assert r.status_code == 200 and r.json()["shared"] is True
        assert w1.receive_json() == {"type": "recording_changed"}
        assert w2.receive_json() == {"type": "recording_changed"}
        assert w2.receive_json() == {"type": "session_ended", "from": "Štěpán Pressl",
                                      "text": "Štěpán Pressl ukončil(a) skupinovou platbu"}
        g = clients[1].post("/api/recording/group", json={"name": "Hospoda"})
        assert g.status_code == 200 and g.json()["members"] == [1, 2]
        types = {w2.receive_json()["type"]}
        assert types == {"group_added"}
        assert w1.receive_json() == {"type": "group_changed", "group_id": g.json()["id"]}
    assert clients[1].post("/api/recording/discard").status_code == 200


def test_http_decline(clients):
    clients[1].post("/api/recording/start", json={"invite": [2]})
    with clients[1].websocket_connect("/ws") as w1:
        assert clients[2].post("/api/recording/invites/1/decline").status_code == 200
        assert w1.receive_json() == {"type": "recording_changed"}
    assert clients[2].post("/api/recording/invites/1/decline").status_code == 400


def test_cancelled_invites_get_group_changed_on_approve_and_delete(clients):
    g = clients[1].post("/api/groups", json={"name": "G", "members": [2, 3]}).json()
    with clients[2].websocket_connect("/ws") as w2, clients[3].websocket_connect("/ws") as w3:
        assert clients[1].post(f"/api/groups/{g['id']}/approve").status_code == 200
        assert w2.receive_json() == {"type": "group_changed", "group_id": g["id"]}
        assert w3.receive_json() == {"type": "group_changed", "group_id": g["id"]}
    g = clients[1].post("/api/groups", json={"name": "H", "members": [2]}).json()
    with clients[2].websocket_connect("/ws") as w2:
        assert clients[1].delete(f"/api/groups/{g['id']}").status_code == 200
        assert w2.receive_json() == {"type": "group_changed", "group_id": g["id"]}


def test_migrates_old_recordings_table(tmp_path):
    import sqlite3
    path = str(tmp_path / "old.db")
    init_db(path)
    c = sqlite3.connect(path)
    c.execute("DROP TABLE recordings")
    c.execute("CREATE TABLE recordings (person INTEGER PRIMARY KEY, started_at TEXT NOT NULL)")
    c.execute("INSERT INTO recordings VALUES (1, '2026-01-01T10:00:00')")
    c.commit()
    c.close()
    init_db(path)
    rec = recording(path, 1)
    assert rec["starter"] == 1 and rec["participants"] == [1]
