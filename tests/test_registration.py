import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app


def make_app():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    return create_app(database_path=path), path


def test_c1_create_direct_activity():
    app, _ = make_app()
    client = app.test_client()
    resp = client.post("/api/activities", json={
        "title": "迎新晚会", "category": "文艺", "location": "礼堂",
        "capacity": 2, "policy_type": "DIRECT"
    })
    assert resp.status_code == 201
    assert resp.get_json()["activity_id"] > 0


def test_c2_direct_register_approved_and_notify():
    app, _ = make_app()
    client = app.test_client()
    aid = client.post("/api/activities", json={
        "title": "篮球赛", "capacity": 2, "policy_type": "DIRECT"
    }).get_json()["activity_id"]
    resp = client.post("/api/register", json={"activity_id": aid, "student_id": "s001"})
    assert resp.status_code == 201
    assert resp.get_json()["status"] == "APPROVED"
    msgs = client.get("/api/messages/s001").get_json()
    assert len(msgs) == 1


def test_c3_duplicate_registration_rejected():
    app, _ = make_app()
    client = app.test_client()
    aid = client.post("/api/activities", json={"title": "讲座", "capacity": 5, "policy_type": "DIRECT"}).get_json()["activity_id"]
    client.post("/api/register", json={"activity_id": aid, "student_id": "s001"})
    resp = client.post("/api/register", json={"activity_id": aid, "student_id": "s001"})
    assert resp.status_code == 400


def test_c4_full_capacity_blocks_next():
    app, _ = make_app()
    client = app.test_client()
    aid = client.post("/api/activities", json={"title": " workshop", "capacity": 1, "policy_type": "DIRECT"}).get_json()["activity_id"]
    client.post("/api/register", json={"activity_id": aid, "student_id": "s001"})
    resp = client.post("/api/register", json={"activity_id": aid, "student_id": "s002"})
    assert resp.status_code == 400


def test_c5_review_activity_pending():
    app, _ = make_app()
    client = app.test_client()
    aid = client.post("/api/activities", json={"title": "志愿者", "capacity": 3, "policy_type": "REVIEW"}).get_json()["activity_id"]
    resp = client.post("/api/register", json={"activity_id": aid, "student_id": "s001"})
    assert resp.get_json()["status"] == "PENDING"


def test_c6_admin_approve_pending():
    app, _ = make_app()
    client = app.test_client()
    aid = client.post("/api/activities", json={"title": "社团招新", "capacity": 2, "policy_type": "REVIEW"}).get_json()["activity_id"]
    rid = client.post("/api/register", json={"activity_id": aid, "student_id": "s001"}).get_json()["registration_id"]
    resp = client.post(f"/api/registrations/{rid}/review", json={"approve": True})
    assert resp.get_json()["status"] == "APPROVED"
    assert len(client.get("/api/messages/s001").get_json()) == 2


def test_c7_admin_reject_pending():
    app, _ = make_app()
    client = app.test_client()
    aid = client.post("/api/activities", json={"title": "竞赛", "capacity": 2, "policy_type": "REVIEW"}).get_json()["activity_id"]
    rid = client.post("/api/register", json={"activity_id": aid, "student_id": "s001"}).get_json()["registration_id"]
    resp = client.post(f"/api/registrations/{rid}/review", json={"approve": False})
    assert resp.get_json()["status"] == "REJECTED"


def test_c8_approve_when_full_fails():
    app, _ = make_app()
    client = app.test_client()
    aid = client.post("/api/activities", json={"title": "限额活动", "capacity": 1, "policy_type": "REVIEW"}).get_json()["activity_id"]
    rid1 = client.post("/api/register", json={"activity_id": aid, "student_id": "s001"}).get_json()["registration_id"]
    rid2 = client.post("/api/register", json={"activity_id": aid, "student_id": "s002"}).get_json()["registration_id"]
    client.post(f"/api/registrations/{rid1}/review", json={"approve": True})
    resp = client.post(f"/api/registrations/{rid2}/review", json={"approve": True})
    assert resp.status_code == 400


def test_c9_cancel_registration():
    app, _ = make_app()
    client = app.test_client()
    aid = client.post("/api/activities", json={"title": "展览", "capacity": 2, "policy_type": "DIRECT"}).get_json()["activity_id"]
    rid = client.post("/api/register", json={"activity_id": aid, "student_id": "s001"}).get_json()["registration_id"]
    resp = client.post(f"/api/registrations/{rid}/cancel")
    assert resp.get_json()["status"] == "CANCELLED"
    stats = client.get(f"/api/activities/{aid}").get_json()["stats"]
    assert stats["approved"] == 0


def test_c10_data_persists_after_restart():
    app, path = make_app()
    client = app.test_client()
    aid = client.post("/api/activities", json={"title": "持久化活动", "capacity": 2, "policy_type": "DIRECT"}).get_json()["activity_id"]
    client.post("/api/register", json={"activity_id": aid, "student_id": "s001"})

    app2 = create_app(database_path=path)
    client2 = app2.test_client()
    detail = client2.get(f"/api/activities/{aid}").get_json()
    assert detail["title"] == "持久化活动"
    assert len(detail["registrations"]) == 1
