# Shared FastAPI dependencies
# Currently auth dependencies live in app/services/auth.py and app/services/permissions.py
# This file is reserved for future shared dependencies

from app.services.auth import get_current_user
from app.services.permissions import get_admin, get_editor_or_admin, require_role

__all__ = ["get_current_user", "get_admin", "get_editor_or_admin", "require_role"]
