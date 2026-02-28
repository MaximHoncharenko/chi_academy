#!/usr/bin/env python3
"""
Management command to create a new user.

Usage (locally):
    python scripts/create_user.py --username john --email john@example.com --password secret123 --role user

Usage (via Docker):
    docker compose exec api python scripts/create_user.py --username john --email john@example.com --password secret123 --role admin
"""
import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import SessionLocal
from app.models.user import User, UserRole
from app.services.auth import hash_password


def create_user(username: str, email: str, password: str, role: str):
    db = SessionLocal()
    try:
        existing = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        if existing:
            print(f"[ERROR] User '{username}' or email '{email}' already exists.")
            sys.exit(1)

        user = User(
            username=username,
            email=email,
            hashed_password=hash_password(password),
            role=UserRole(role),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"[OK] Created user '{username}' with role '{role}' (id={user.id})")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a new user")
    parser.add_argument("--username", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--role", required=True, choices=["user", "editor", "admin"])
    args = parser.parse_args()
    create_user(args.username, args.email, args.password, args.role)
