# Articles REST API

FastAPI + PostgreSQL + JWT Auth + Role-Based Access Control

## Stack
- FastAPI, PostgreSQL, SQLAlchemy, Alembic, JWT, bcrypt, pytest

## Quick Start

### 1. Configure environment
    cp .env.example .env

### 2. Start with Docker
    docker compose up --build

API: http://localhost:8000
Docs: http://localhost:8000/docs

## Default Users (seeded automatically)

| Username      | Password     | Role   |
|---------------|--------------|--------|
| admin_user    | Admin1234!   | admin  |
| editor_user   | Editor1234!  | editor |
| regular_user  | User1234!    | user   |

## Create User (management command)
    docker compose exec api python scripts/create_user.py --username john --email john@example.com --password pass123 --role user

## Run Tests
    pytest -v --cov=app --cov-report=term-missing

## Alembic Migrations
    docker compose exec api alembic upgrade head
    docker compose exec api alembic revision --autogenerate -m "description"

## API Endpoints

### Auth
| Method | Endpoint    | Access  |
|--------|-------------|---------|
| POST   | /auth/login | Public  |

### Users (Admin only)
| Method | Endpoint         | Description      |
|--------|------------------|------------------|
| GET    | /users/          | List users       |
| GET    | /users/me        | Current user     |
| GET    | /users/search    | Search by text   |
| GET    | /users/{id}      | Get by ID        |
| POST   | /users/          | Create user      |
| PUT    | /users/{id}      | Update user      |
| DELETE | /users/{id}      | Delete user      |

### Articles (All authenticated)
| Method | Endpoint            | Access                  |
|--------|---------------------|-------------------------|
| GET    | /articles/          | All                     |
| GET    | /articles/search    | All                     |
| GET    | /articles/{id}      | All                     |
| POST   | /articles/          | All                     |
| PUT    | /articles/{id}      | Owner / Editor / Admin  |
| DELETE | /articles/{id}      | Owner / Admin           |

All list endpoints support ?limit=N&offset=N pagination.

## Role Permissions

| Action                  | user | editor | admin |
|-------------------------|------|--------|-------|
| View any article        | yes  | yes    | yes   |
| Create article          | yes  | yes    | yes   |
| Update own article      | yes  | yes    | yes   |
| Update any article      | no   | yes    | yes   |
| Delete own article      | yes  | no     | yes   |
| Delete any article      | no   | no     | yes   |
| Manage users            | no   | no     | yes   |
