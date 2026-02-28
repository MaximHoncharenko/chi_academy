import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.user import User, UserRole
from app.models.article import Article
from app.services.auth import hash_password, create_access_token

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, _):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    return TestClient(app)


def make_user(db, username, email, role: UserRole, password: str = "testpass") -> User:
    user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def token_for(user: User) -> str:
    return create_access_token({"sub": user.username, "role": user.role.value})


def auth_headers(user: User) -> dict:
    return {"Authorization": f"Bearer {token_for(user)}"}


@pytest.fixture
def admin_user(db):
    return make_user(db, "admin", "admin@test.com", UserRole.admin)


@pytest.fixture
def editor_user(db):
    return make_user(db, "editor", "editor@test.com", UserRole.editor)


@pytest.fixture
def regular_user(db):
    return make_user(db, "user1", "user1@test.com", UserRole.user)


@pytest.fixture
def another_user(db):
    return make_user(db, "user2", "user2@test.com", UserRole.user)


@pytest.fixture
def sample_article(db, regular_user):
    article = Article(
        title="Test Article",
        content="Test content here.",
        author_id=regular_user.id,
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    return article
