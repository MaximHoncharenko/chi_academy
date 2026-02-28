from tests.conftest import auth_headers


def test_login_success(client, regular_user):
    resp = client.post("/auth/login", data={"username": "user1", "password": "testpass"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, regular_user):
    resp = client.post("/auth/login", data={"username": "user1", "password": "wrong"})
    assert resp.status_code == 401


def test_login_nonexistent_user(client):
    resp = client.post("/auth/login", data={"username": "ghost", "password": "pass"})
    assert resp.status_code == 401


def test_protected_route_no_token(client):
    resp = client.get("/users/me")
    assert resp.status_code == 401


def test_protected_route_invalid_token(client):
    resp = client.get("/users/me", headers={"Authorization": "Bearer invalid.token.here"})
    assert resp.status_code == 401


def test_protected_route_with_token(client, regular_user):
    resp = client.get("/users/me", headers=auth_headers(regular_user))
    assert resp.status_code == 200
    assert resp.json()["username"] == "user1"
