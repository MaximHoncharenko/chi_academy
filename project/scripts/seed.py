#!/usr/bin/env python3
"""
Seed script — populates the DB with sample users and articles.
Passwords are properly bcrypt-hashed at runtime.

Usage:
    python scripts/seed.py
    docker compose exec api python scripts/seed.py
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import SessionLocal, Base, engine
from app.models.user import User, UserRole
from app.models.article import Article
from app.services.auth import hash_password

Base.metadata.create_all(bind=engine)

USERS = [
    {"username": "admin_user",   "email": "admin@example.com",  "password": "Admin1234!",  "role": UserRole.admin},
    {"username": "editor_user",  "email": "editor@example.com", "password": "Editor1234!", "role": UserRole.editor},
    {"username": "regular_user", "email": "user@example.com",   "password": "User1234!",   "role": UserRole.user},
]

ARTICLES = [
    {
        "title": "Getting Started with FastAPI",
        "content": "FastAPI is a modern, fast web framework for building APIs with Python 3.7+ "
                   "based on standard Python type hints.",
        "author": "admin_user",
    },
    {
        "title": "SQLAlchemy ORM Basics",
        "content": "SQLAlchemy provides a full suite of well-known enterprise-level persistence "
                   "patterns. In this article we explore the ORM layer.",
        "author": "editor_user",
    },
    {
        "title": "My First Article",
        "content": "This is a sample article written by a regular user. "
                   "All user roles can create and manage their own content.",
        "author": "regular_user",
    },
]


def seed():
    db = SessionLocal()
    try:
        print("Seeding users...")
        user_map = {}
        for u in USERS:
            existing = db.query(User).filter(User.username == u["username"]).first()
            if not existing:
                new_user = User(
                    username=u["username"],
                    email=u["email"],
                    hashed_password=hash_password(u["password"]),
                    role=u["role"],
                )
                db.add(new_user)
                db.flush()
                user_map[u["username"]] = new_user
                print(f"  + Created: {u['username']} ({u['role'].value}) | password: {u['password']}")
            else:
                user_map[u["username"]] = existing
                print(f"  - Skipped (exists): {u['username']}")
        db.commit()

        print("Seeding articles...")
        for a in ARTICLES:
            author = user_map.get(a["author"])
            if author:
                db.add(Article(title=a["title"], content=a["content"], author_id=author.id))
                print(f"  + Created: '{a['title']}'")
        db.commit()

        print("")
        print("Seed completed. Default credentials:")
        print("  admin_user   / Admin1234!  (admin)")
        print("  editor_user  / Editor1234! (editor)")
        print("  regular_user / User1234!   (user)")
    except Exception as e:
        db.rollback()
        print(f"Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
