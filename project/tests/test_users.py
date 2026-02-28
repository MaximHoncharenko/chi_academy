from tests.conftest import auth_headers


def test_list_users_as_admin(client, admin_user, regular_user):
    resp = client.get("/users/", headers=auth_headers(admin_user))
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_list_users_forbidden_for_user(client, regular_user):
    resp = client.get("/users/", headers=auth_headers(regular_user))
    assert resp.status_code == 403


def test_list_users_forbidden_for_editor(client, editor_user):
    resp = client.get("/users/", headers=auth_headers(editor_user))
    assert resp.status_code == 403


def test_get_user_by_id(client, admin_user, regular_user):
    resp = client.get(f"/users/{regular_user.id}", headers=auth_headers(admin_user))
    assert resp.status_code == 200
    assert resp.json()["username"] == "user1"


def test_get_user_not_found(client, admin_user):
    resp = client.get("/users/99999", headers=auth_headers(admin_user))
    assert resp.status_code == 404


def test_create_user_as_admin(client, admin_user):
    resp = client.post(
        "/users/",
        json={"username": "newuser", "email": "new@test.com", "password": "pass123", "role": "user"},
        headers=auth_headers(admin_user),
    )
    assert resp.status_code == 201
    assert resp.json()["username"] == "newuser"
    assert resp.json()["role"] == "user"


def test_create_user_forbidden_for_regular(client, regular_user):
    resp = client.post(
        "/users/",
        json={"username": "x", "email": "x@x.com", "password": "pass", "role": "user"},
        headers=auth_headers(regular_user),
    )
    assert resp.status_code == 403


def test_create_user_duplicate(client, admin_user, regular_user):
    resp = client.post(
        "/users/",
        json={"username": "user1", "email": "other@test.com", "password": "pass", "role": "user"},
        headers=auth_headers(admin_user),
    )
    assert resp.status_code == 409


def test_update_user(client, admin_user, regular_user):
    resp = client.put(
        f"/users/{regular_user.id}",
        json={"username": "updated_user"},
        headers=auth_headers(admin_user),
    )
    assert resp.status_code == 200
    assert resp.json()["username"] == "updated_user"


def test_update_user_not_found(client, admin_user):
    resp = client.put("/users/99999", json={"username": "x"}, headers=auth_headers(admin_user))
    assert resp.status_code == 404


def test_update_user_password(client, admin_user, regular_user):
    resp = client.put(
        f"/users/{regular_user.id}",
        json={"password": "newpassword123"},
        headers=auth_headers(admin_user),
    )
    assert resp.status_code == 200


def test_delete_user(client, admin_user, regular_user):
    resp = client.delete(f"/users/{regular_user.id}", headers=auth_headers(admin_user))
    assert resp.status_code == 204


def test_delete_user_not_found(client, admin_user):
    resp = client.delete("/users/99999", headers=auth_headers(admin_user))
    assert resp.status_code == 404


def test_search_users(client, admin_user, regular_user):
    resp = client.get("/users/search?q=user1", headers=auth_headers(admin_user))
    assert resp.status_code == 200
    assert any(u["username"] == "user1" for u in resp.json())


def test_search_users_by_email(client, admin_user, regular_user):
    resp = client.get("/users/search?q=user1@test", headers=auth_headers(admin_user))
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_search_users_no_results(client, admin_user):
    resp = client.get("/users/search?q=xxxxnotexist", headers=auth_headers(admin_user))
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_users_pagination(client, admin_user, regular_user, editor_user):
    resp = client.get("/users/?limit=1&offset=0", headers=auth_headers(admin_user))
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_get_me(client, regular_user):
    resp = client.get("/users/me", headers=auth_headers(regular_user))
    assert resp.status_code == 200
    assert resp.json()["id"] == regular_user.id


def test_get_me_unauthenticated(client):
    resp = client.get("/users/me")
    assert resp.status_code == 401
