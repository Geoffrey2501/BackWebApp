"""Tests for /subscriber endpoints."""


def test_register_subscriber(client):
    resp = client.post("/subscriber/register", json={
        "first_name": "Alice",
        "last_name": "Dupont",
        "email": "alice@test.com",
        "child_age_range": "PE",
        "category_preferences": ["SOC", "FIG", "EVL", "CON", "LIV", "EXT"],
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["id"] == "s1"
    assert data["email"] == "alice@test.com"
    assert data["child_age_range"] == "PE"


def test_register_validation(client):
    resp = client.post("/subscriber/register", json={
        "first_name": "",
        "last_name": "",
        "email": "invalid",
        "child_age_range": "XX",
        "category_preferences": ["SOC"],
    })
    assert resp.status_code == 400
    errors = resp.get_json()["errors"]
    assert len(errors) >= 3


def test_register_updates_existing(client):
    """Registering same email again updates the subscriber."""
    client.post("/subscriber/register", json={
        "first_name": "Alice",
        "last_name": "Dupont",
        "email": "alice@test.com",
        "child_age_range": "PE",
        "category_preferences": ["SOC", "FIG", "EVL", "CON", "LIV", "EXT"],
    })
    resp = client.post("/subscriber/register", json={
        "first_name": "Alice",
        "last_name": "Martin",
        "email": "alice@test.com",
        "child_age_range": "EN",
        "category_preferences": ["EXT", "CON", "SOC", "EVL", "FIG", "LIV"],
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["id"] == "s1"  # Same ID
    assert data["child_age_range"] == "EN"


def test_update_preferences(client):
    client.post("/subscriber/register", json={
        "first_name": "Alice",
        "last_name": "Dupont",
        "email": "alice@test.com",
        "child_age_range": "PE",
        "category_preferences": ["SOC", "FIG", "EVL", "CON", "LIV", "EXT"],
    })
    resp = client.put("/subscriber/preferences", json={
        "email": "alice@test.com",
        "child_age_range": "EN",
        "category_preferences": ["EXT", "CON", "SOC", "EVL", "FIG", "LIV"],
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["child_age_range"] == "EN"
    assert data["category_preferences"][0] == "EXT"


def test_update_preferences_not_found(client):
    resp = client.put("/subscriber/preferences", json={
        "email": "nobody@test.com",
    })
    assert resp.status_code == 404


def test_list_subscribers_admin(client):
    client.post("/subscriber/register", json={
        "first_name": "Alice",
        "last_name": "Dupont",
        "email": "alice@test.com",
        "child_age_range": "PE",
        "category_preferences": ["SOC", "FIG", "EVL", "CON", "LIV", "EXT"],
    })
    resp = client.get("/admin/subscribers")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 1
    assert data[0]["first_name"] == "Alice"


def test_subscriber_box_not_found(client):
    resp = client.get("/subscriber/box?email=nobody@test.com")
    assert resp.status_code == 404


def test_subscriber_history_empty(client):
    client.post("/subscriber/register", json={
        "first_name": "Alice",
        "last_name": "Dupont",
        "email": "alice@test.com",
        "child_age_range": "PE",
        "category_preferences": ["SOC", "FIG", "EVL", "CON", "LIV", "EXT"],
    })
    resp = client.get("/subscriber/history?email=alice@test.com")
    assert resp.status_code == 200
    assert resp.get_json() == []
