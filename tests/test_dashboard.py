"""Tests for /admin/dashboard and /admin/history endpoints."""


def test_dashboard_empty(client):
    resp = client.get("/admin/dashboard")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["total_articles"] == 0
    assert data["active_subscribers"] == 0


def test_dashboard_with_data(client, sample_articles, sample_subscribers):
    resp = client.get("/admin/dashboard")
    data = resp.get_json()
    assert data["total_articles"] == 8
    assert data["active_subscribers"] == 3
    assert data["articles_by_category"]["SOC"] == 1
    assert data["articles_by_category"]["CON"] == 2
    assert data["subscribers_by_age_range"]["PE"] == 2
    assert data["subscribers_by_age_range"]["EN"] == 1


def test_history_empty(client):
    resp = client.get("/admin/history")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_history_after_validation(client, sample_articles, sample_subscribers):
    # Create + optimize + validate
    resp = client.post("/admin/campaigns", json={"max_weight_per_box": 1200})
    cid = resp.get_json()["id"]
    client.post(f"/admin/campaigns/{cid}/optimize")

    resp = client.get(f"/admin/campaigns/{cid}/boxes")
    boxes = resp.get_json()
    for box in boxes:
        client.post(f"/admin/campaigns/{cid}/boxes/{box['subscriber_id']}/validate")

    resp = client.get("/admin/history")
    data = resp.get_json()
    assert len(data) == 1
    assert data[0]["campaign_id"] == cid
    assert data[0]["nb_boxes"] == 3


def test_subscriber_box_after_validation(client, sample_articles, sample_subscribers):
    resp = client.post("/admin/campaigns", json={"max_weight_per_box": 1200})
    cid = resp.get_json()["id"]
    client.post(f"/admin/campaigns/{cid}/optimize")

    # Validate all
    resp = client.get(f"/admin/campaigns/{cid}/boxes")
    boxes = resp.get_json()
    for box in boxes:
        client.post(f"/admin/campaigns/{cid}/boxes/{box['subscriber_id']}/validate")

    # Check subscriber can see their box
    resp = client.get("/subscriber/box?email=alice@test.com")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["validated"] is True
    assert "articles" in data


def test_subscriber_history_after_validation(client, sample_articles, sample_subscribers):
    resp = client.post("/admin/campaigns", json={"max_weight_per_box": 1200})
    cid = resp.get_json()["id"]
    client.post(f"/admin/campaigns/{cid}/optimize")

    resp = client.get(f"/admin/campaigns/{cid}/boxes")
    boxes = resp.get_json()
    for box in boxes:
        client.post(f"/admin/campaigns/{cid}/boxes/{box['subscriber_id']}/validate")

    resp = client.get("/subscriber/history?email=alice@test.com")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 1
