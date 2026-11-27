import pytest
from fastapi.testclient import TestClient

from server.app import create_app
from server.db import (
    PaymentError,
    accept_group_invite,
    add_expense,
    approve_group,
    create_group,
    decline_group_invite,
    delete_expense,
    group_invites_for,
    groups_for,
    init_db,
    requests_by,
)
from server.orchestrator import Orchestrator


@pytest.fixture
def db(tmp_path):
    path = str(tmp_path / "t.db")
    init_db(path)
    return path


def test_create_invites_members(db):
    g = create_group(db, 1, "Chata", [2, 3])
    assert g["members"] == [1] and g["invited"] == [2, 3]
    mine = groups_for(db, 1)
    assert [x["id"] for x in mine] == [g["id"]] and mine[0]["invited"] == [2, 3]
    assert groups_for(db, 2) == []
    assert [x["id"] for x in group_invites_for(db, 2)] == [g["id"]]
    assert group_invites_for(db, 1) == []


def test_accepted_flag_skips_invites(db):
    g = create_group(db, 1, "Chata", [2], accepted=True)
    assert g["members"] == [1, 2] and g["invited"] == []


def test_accept(db):
    g = create_group(db, 1, "Chata", [2])
    done = accept_group_invite(db, g["id"], 2)
    assert done["members"] == [1, 2] and done["invited"] == []
    assert [x["id"] for x in groups_for(db, 2)] == [g["id"]]
    assert group_invites_for(db, 2) == []


def test_decline(db):
    g = create_group(db, 1, "Chata", [2, 3])
    assert decline_group_invite(db, g["id"], 2) == {"id": g["id"], "name": "Chata", "creator": 1}
    assert groups_for(db, 2) == [] and group_invites_for(db, 2) == []
    assert groups_for(db, 1)[0]["invited"] == [3]


def test_invited_person_cannot_act(db):
    g = create_group(db, 1, "Chata", [2])
    add_expense(db, g["id"], 1, 100, "Food")
    eid = groups_for(db, 1)[0]["expenses"][0]["id"]
    for call in (
        lambda: add_expense(db, g["id"], 2, 50, "x"),
        lambda: approve_group(db, g["id"], 2),
        lambda: delete_expense(db, g["id"], eid, 2),
    ):
        with pytest.raises(PaymentError, match="Skupina nebyla nalezena"):
            call()


def test_approve_ignores_invited_and_removes_invites(db):
    g = create_group(db, 1, "Chata", [2, 3])
    accept_group_invite(db, g["id"], 2)
    add_expense(db, g["id"], 1, 300, "Food")
    done = approve_group(db, g["id"], 1)
    assert done["cancelled_invites"] == [3]
    assert done["invited"] == [] and done["members"] == [1, 2]
    assert {(r["requester"], r["payer"]) for r in done["requests"]} == {(1, 2)}
    assert group_invites_for(db, 3) == []
    assert requests_by(db, 3) == []


@pytest.mark.parametrize("fn", [accept_group_invite, decline_group_invite])
def test_no_invite(db, fn):
    g = create_group(db, 1, "Chata", [2])
    for who in (3, 1):
        with pytest.raises(PaymentError, match="Pozvánka nebyla nalezena"):
            fn(db, g["id"], who)
    with pytest.raises(PaymentError, match="Pozvánka nebyla nalezena"):
        fn(db, 999, 2)


def test_accept_after_approval_fails(db):
    g = create_group(db, 1, "Chata", [2])
    approve_group(db, g["id"], 1)
    with pytest.raises(PaymentError):
        accept_group_invite(db, g["id"], 2)


def test_accept_twice_fails(db):
    g = create_group(db, 1, "Chata", [2])
    accept_group_invite(db, g["id"], 2)
    with pytest.raises(PaymentError, match="Pozvánka nebyla nalezena"):
        accept_group_invite(db, g["id"], 2)


def test_delete_group_removes_invites(db):
    from server.db import delete_group
    g = create_group(db, 1, "Chata", [2])
    delete_group(db, g["id"], 1)
    assert group_invites_for(db, 2) == []


@pytest.fixture
def clients(tmp_path):
    path = str(tmp_path / "t.db")
    init_db(path)
    orch = Orchestrator()
    return {n: TestClient(create_app(n, orch, path)) for n in (1, 2, 3, 4)}


def test_invite_endpoints(clients):
    with clients[2].websocket_connect("/ws") as ws2, clients[1].websocket_connect("/ws") as ws1:
        gid = clients[1].post("/api/groups", json={"name": "Chata", "members": [2]}).json()["id"]
        ev = ws2.receive_json()
        assert ev["type"] == "group_invite" and ev["group"]["id"] == gid
        assert ev["text"] == "Štěpán Pressl tě zve do skupiny Chata"
        assert ws1.receive_json()["type"] == "group_changed"
        s = clients[2].get("/api/state").json()
        assert s["groups"] == [] and [g["id"] for g in s["group_invites"]] == [gid]
        assert clients[2].post(f"/api/groups/{gid}/accept").status_code == 200
        assert ws1.receive_json() == {"type": "group_changed", "group_id": gid}
        assert ws2.receive_json() == {"type": "group_changed", "group_id": gid}
    s = clients[2].get("/api/state").json()
    assert [g["id"] for g in s["groups"]] == [gid] and s["group_invites"] == []


def test_decline_endpoint(clients):
    gid = clients[1].post("/api/groups", json={"name": "Chata", "members": [2]}).json()["id"]
    with clients[1].websocket_connect("/ws") as ws1:
        assert clients[2].post(f"/api/groups/{gid}/decline").status_code == 200
        assert ws1.receive_json()["type"] == "group_changed"
    assert clients[2].get("/api/state").json()["group_invites"] == []
    assert clients[2].post(f"/api/groups/{gid}/decline").status_code == 400
    assert clients[3].post(f"/api/groups/{gid}/accept").status_code == 400
