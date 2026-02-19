"""Tests for /admin/articles endpoints."""



def test_create_article(client):
    resp = client.post("/admin/articles", json={
        "designation": "Monopoly Junior",
        "category": "SOC",
        "age_range": "PE",
        "condition": "N",
        "price": 8,
        "weight": 400,
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["id"] == "a1"
    assert data["designation"] == "Monopoly Junior"
    assert data["category"] == "SOC"


def test_create_article_validation(client):
    resp = client.post("/admin/articles", json={
        "designation": "",
        "category": "INVALID",
        "age_range": "XX",
        "condition": "Z",
        "price": -1,
        "weight": 0,
    })
    assert resp.status_code == 400
    errors = resp.get_json()["errors"]
    assert len(errors) >= 4


def test_list_articles_paginated(client):
    # Create 12 articles
    for i in range(12):
        client.post("/admin/articles", json={
            "designation": f"Article {i}",
            "category": "SOC",
            "age_range": "PE",
            "condition": "N",
            "price": 5,
            "weight": 200,
        })

    resp = client.get("/admin/articles?page=1")
    data = resp.get_json()
    assert data["total"] == 12
    assert len(data["items"]) == 10
    assert data["total_pages"] == 2

    resp = client.get("/admin/articles?page=2")
    data = resp.get_json()
    assert len(data["items"]) == 2


def test_list_articles_filtered(client):
    client.post("/admin/articles", json={
        "designation": "Toy SOC", "category": "SOC",
        "age_range": "PE", "condition": "N", "price": 5, "weight": 200,
    })
    client.post("/admin/articles", json={
        "designation": "Toy FIG", "category": "FIG",
        "age_range": "EN", "condition": "TB", "price": 5, "weight": 200,
    })

    resp = client.get("/admin/articles?category=SOC")
    data = resp.get_json()
    assert data["total"] == 1
    assert data["items"][0]["category"] == "SOC"

    resp = client.get("/admin/articles?age_range=EN")
    data = resp.get_json()
    assert data["total"] == 1

    resp = client.get("/admin/articles?condition=TB")
    data = resp.get_json()
    assert data["total"] == 1


def test_get_article(client):
    client.post("/admin/articles", json={
        "designation": "Test", "category": "SOC",
        "age_range": "PE", "condition": "N", "price": 5, "weight": 200,
    })
    resp = client.get("/admin/articles/a1")
    assert resp.status_code == 200
    assert resp.get_json()["id"] == "a1"


def test_get_article_not_found(client):
    resp = client.get("/admin/articles/a999")
    assert resp.status_code == 404


def test_update_article(client):
    client.post("/admin/articles", json={
        "designation": "Test", "category": "SOC",
        "age_range": "PE", "condition": "N", "price": 5, "weight": 200,
    })
    resp = client.put("/admin/articles/a1", json={"designation": "Updated"})
    assert resp.status_code == 200
    assert resp.get_json()["designation"] == "Updated"


def test_validated_article_removed_from_stock(client, sample_articles, sample_subscribers):
    """Articles in a validated box are removed from stock."""
    # Create campaign and optimize
    resp = client.post("/admin/campaigns", json={"max_weight_per_box": 1200})
    cid = resp.get_json()["id"]
    client.post(f"/admin/campaigns/{cid}/optimize")

    # Get boxes and validate one
    resp = client.get(f"/admin/campaigns/{cid}/boxes")
    boxes = resp.get_json()
    validated_art_ids = []
    for box in boxes:
        if box["article_ids"]:
            client.post(f"/admin/campaigns/{cid}/boxes/{box['subscriber_id']}/validate")
            validated_art_ids = box["article_ids"]
            break

    # Articles should no longer exist in stock
    for art_id in validated_art_ids:
        resp = client.get(f"/admin/articles/{art_id}")
        assert resp.status_code == 404
