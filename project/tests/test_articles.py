from tests.conftest import auth_headers
from app.models.article import Article


def test_create_article(client, regular_user):
    resp = client.post(
        "/articles/",
        json={"title": "New Article", "content": "Content here"},
        headers=auth_headers(regular_user),
    )
    assert resp.status_code == 201
    assert resp.json()["title"] == "New Article"
    assert resp.json()["author_id"] == regular_user.id


def test_create_article_unauthenticated(client):
    resp = client.post("/articles/", json={"title": "x", "content": "y"})
    assert resp.status_code == 401


def test_list_articles(client, regular_user, sample_article):
    resp = client.get("/articles/", headers=auth_headers(regular_user))
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_list_articles_unauthenticated(client):
    resp = client.get("/articles/")
    assert resp.status_code == 401


def test_get_article_by_id(client, regular_user, sample_article):
    resp = client.get(f"/articles/{sample_article.id}", headers=auth_headers(regular_user))
    assert resp.status_code == 200
    assert resp.json()["id"] == sample_article.id
    assert resp.json()["title"] == "Test Article"


def test_get_article_not_found(client, regular_user):
    resp = client.get("/articles/99999", headers=auth_headers(regular_user))
    assert resp.status_code == 404


def test_update_own_article(client, regular_user, sample_article):
    resp = client.put(
        f"/articles/{sample_article.id}",
        json={"title": "Updated Title"},
        headers=auth_headers(regular_user),
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated Title"


def test_update_other_user_article_forbidden(client, another_user, sample_article):
    resp = client.put(
        f"/articles/{sample_article.id}",
        json={"title": "Hack"},
        headers=auth_headers(another_user),
    )
    assert resp.status_code == 403


def test_update_article_not_found(client, regular_user):
    resp = client.put("/articles/99999", json={"title": "x"}, headers=auth_headers(regular_user))
    assert resp.status_code == 404


def test_editor_can_update_any_article(client, editor_user, sample_article):
    resp = client.put(
        f"/articles/{sample_article.id}",
        json={"title": "Editor Updated"},
        headers=auth_headers(editor_user),
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Editor Updated"


def test_admin_can_update_any_article(client, admin_user, sample_article):
    resp = client.put(
        f"/articles/{sample_article.id}",
        json={"title": "Admin Updated"},
        headers=auth_headers(admin_user),
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Admin Updated"


def test_delete_own_article(client, regular_user, sample_article):
    resp = client.delete(f"/articles/{sample_article.id}", headers=auth_headers(regular_user))
    assert resp.status_code == 204


def test_delete_other_user_article_forbidden(client, another_user, sample_article):
    resp = client.delete(f"/articles/{sample_article.id}", headers=auth_headers(another_user))
    assert resp.status_code == 403


def test_admin_can_delete_any_article(client, admin_user, sample_article):
    resp = client.delete(f"/articles/{sample_article.id}", headers=auth_headers(admin_user))
    assert resp.status_code == 204


def test_editor_cannot_delete_article(client, editor_user, sample_article):
    resp = client.delete(f"/articles/{sample_article.id}", headers=auth_headers(editor_user))
    assert resp.status_code == 403


def test_delete_article_not_found(client, regular_user):
    resp = client.delete("/articles/99999", headers=auth_headers(regular_user))
    assert resp.status_code == 404


def test_search_articles(client, regular_user, sample_article):
    resp = client.get("/articles/search?q=Test", headers=auth_headers(regular_user))
    assert resp.status_code == 200
    assert any(a["title"] == "Test Article" for a in resp.json())


def test_search_articles_by_content(client, regular_user, sample_article):
    resp = client.get("/articles/search?q=content", headers=auth_headers(regular_user))
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_search_articles_no_results(client, regular_user):
    resp = client.get("/articles/search?q=xyznotexist", headers=auth_headers(regular_user))
    assert resp.status_code == 200
    assert resp.json() == []


def test_articles_pagination(client, regular_user, db):
    for i in range(5):
        db.add(Article(title=f"Article {i}", content="content", author_id=regular_user.id))
    db.commit()
    resp = client.get("/articles/?limit=2&offset=0", headers=auth_headers(regular_user))
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_articles_pagination_offset(client, regular_user, db):
    for i in range(5):
        db.add(Article(title=f"Article {i}", content="content", author_id=regular_user.id))
    db.commit()
    resp1 = client.get("/articles/?limit=2&offset=0", headers=auth_headers(regular_user))
    resp2 = client.get("/articles/?limit=2&offset=2", headers=auth_headers(regular_user))
    ids1 = {a["id"] for a in resp1.json()}
    ids2 = {a["id"] for a in resp2.json()}
    assert ids1.isdisjoint(ids2)
