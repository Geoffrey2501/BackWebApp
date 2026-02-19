"""Tests for /admin/campaigns endpoints."""


def test_create_campaign(client):
    resp = client.post("/admin/campaigns", json={"max_weight_per_box": 1200})
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["id"] == "c1"
    assert data["status"] == "created"


def test_create_campaign_validation(client):
    resp = client.post("/admin/campaigns", json={"max_weight_per_box": -5})
    assert resp.status_code == 400


def test_list_campaigns(client):
    client.post("/admin/campaigns", json={"max_weight_per_box": 1200})
    client.post("/admin/campaigns", json={"max_weight_per_box": 1500})
    resp = client.get("/admin/campaigns")
    data = resp.get_json()
    assert len(data) == 2


def test_optimize_campaign(client, sample_articles, sample_subscribers):
    resp = client.post("/admin/campaigns", json={"max_weight_per_box": 1200})
    cid = resp.get_json()["id"]

    resp = client.post(f"/admin/campaigns/{cid}/optimize")
    assert resp.status_code == 200
    boxes = resp.get_json()
    assert len(boxes) == 3  # One per subscriber


def test_optimize_already_optimized(client, sample_articles, sample_subscribers):
    resp = client.post("/admin/campaigns", json={"max_weight_per_box": 1200})
    cid = resp.get_json()["id"]

    client.post(f"/admin/campaigns/{cid}/optimize")
    resp = client.post(f"/admin/campaigns/{cid}/optimize")
    assert resp.status_code == 400


def test_get_boxes(client, sample_articles, sample_subscribers):
    resp = client.post("/admin/campaigns", json={"max_weight_per_box": 1200})
    cid = resp.get_json()["id"]
    client.post(f"/admin/campaigns/{cid}/optimize")

    resp = client.get(f"/admin/campaigns/{cid}/boxes")
    assert resp.status_code == 200
    boxes = resp.get_json()
    assert len(boxes) == 3
    # Each box should have articles detail
    for box in boxes:
        assert "articles" in box
        assert "subscriber_name" in box


def test_validate_box(client, sample_articles, sample_subscribers):
    resp = client.post("/admin/campaigns", json={"max_weight_per_box": 1200})
    cid = resp.get_json()["id"]
    client.post(f"/admin/campaigns/{cid}/optimize")

    resp = client.get(f"/admin/campaigns/{cid}/boxes")
    boxes = resp.get_json()
    sub_id = boxes[0]["subscriber_id"]

    resp = client.post(f"/admin/campaigns/{cid}/boxes/{sub_id}/validate")
    assert resp.status_code == 200
    assert resp.get_json()["validated"] is True


def test_validate_box_twice(client, sample_articles, sample_subscribers):
    resp = client.post("/admin/campaigns", json={"max_weight_per_box": 1200})
    cid = resp.get_json()["id"]
    client.post(f"/admin/campaigns/{cid}/optimize")

    resp = client.get(f"/admin/campaigns/{cid}/boxes")
    sub_id = resp.get_json()[0]["subscriber_id"]

    client.post(f"/admin/campaigns/{cid}/boxes/{sub_id}/validate")
    resp = client.post(f"/admin/campaigns/{cid}/boxes/{sub_id}/validate")
    assert resp.status_code == 400
