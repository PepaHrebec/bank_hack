import time

import pytest
from fastapi.testclient import TestClient

from server import db, demo
from server.app import create_app


def wait_for(fn, timeout=2):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        if fn():
            return True
        time.sleep(0.02)
    return fn()


@pytest.fixture
def setup(tmp_path):
    demo.add_david()
    path = str(tmp_path / "d.db")
    db.init_db(path)
    orch = demo.DemoOrchestrator(path, delay=0)
    with TestClient(create_app(demo.DAVID, orch, path)) as client:
        yield client, orch, path
    demo.remove_david()


def state(client):
    return client.get("/api/state").json()


def befriend(client, ids):
    for i in ids:
        assert client.post("/api/friends", json={"account": f"{str(i) * 10}/0800"}).status_code == 200
    assert wait_for(lambda: set(state(client)["friends"]) >= set(ids))


def test_friend_request_accepted(setup):
    client, _, _ = setup
    befriend(client, [1])


def test_group_invites_accepted_and_shares_paid(setup):
    client, _, _ = setup
    befriend(client, [1, 2, 3, 4])
    start = state(client)["balance"]
    gid = client.post("/api/groups", json={"name": "Chata", "members": [1, 2, 3, 4]}).json()["id"]
    group = lambda: next(g for g in state(client)["groups"] if g["id"] == gid)
    assert wait_for(lambda: group()["invited"] == [])
    assert client.post(f"/api/groups/{gid}/expenses", json={"amount": 4000, "description": "ubytování"}).status_code == 200
    assert client.post(f"/api/groups/{gid}/approve").status_code == 200
    assert wait_for(lambda: state(client)["balance"] == start + 3200)
    assert all(r["status"] == "paid" for r in state(client)["requested"])


def test_bot_pays_manual_request(setup):
    client, _, _ = setup
    befriend(client, [2])
    assert client.post("/api/requests", json={"payer": 2, "amount": 250, "note": "kino"}).status_code == 200
    assert wait_for(lambda: [r["status"] for r in state(client)["requested"]] == ["paid"])


def test_session_invite_and_stepan_pays_once(setup):
    client, _, _ = setup
    befriend(client, [1])
    assert client.post("/api/recording/start", json={"invite": [1]}).status_code == 200
    assert wait_for(lambda: state(client)["recording"]["participants"] == [5, 1])
    client.post("/api/card-payments", json={"amount": 1240, "note": "Lokál"})
    client.post("/api/card-payments", json={"amount": 300, "note": "Kafe"})
    time.sleep(0.3)
    result = client.post("/api/recording/stop").json()
    assert sorted(p["person"] for p in result["payments"]) == [1, 5, 5]
    assert [p["note"] for p in result["payments"] if p["person"] == 1] == ["Benzina"]


def test_reset_cancels_pending_bot_actions(tmp_path):
    demo.add_david()
    path = str(tmp_path / "d.db")
    db.init_db(path)
    orch = demo.DemoOrchestrator(path, delay=0.3)
    try:
        with TestClient(create_app(demo.DAVID, orch, path)) as client:
            client.post("/api/friends", json={"account": "1111111111/0800"})
            orch.cancel_all()
            demo.seed_demo(path)
            time.sleep(0.5)
            s = state(client)
            assert s["friends"] == [] and s["friend_requests_sent"] == []
    finally:
        demo.remove_david()
