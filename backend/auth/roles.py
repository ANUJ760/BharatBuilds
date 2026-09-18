"""Viewer / Editor / Owner role enforcement and FastAPI auth dependencies.

Provides role hierarchy validation and dependency injection helpers:
- ``get_current_user``: extracts and verifies Cognito JWT from Bearer header
- ``require_role(min_role)``: enforces minimum role permission (403 on insufficient privilege)
- ``require_viewer``, ``require_editor``, ``require_owner``
"""

from __future__ import annotations

from typing import Any, Callable

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.auth.cognito_client import verify_cognito_token
from backend.models.app import Role

ROLES = {"viewer", "editor", "owner"}

_ROLE_HIERARCHY = {
    Role.VIEWER.value: 0,
    Role.EDITOR.value: 1,
    Role.OWNER.value: 2,
}

security_bearer = HTTPBearer(auto_error=False)


def check_permission(user_role: str | Role, required_role: str | Role) -> bool:
    """Check if user_role meets or exceeds the required_role level."""
    u_role = user_role.value if isinstance(user_role, Role) else str(user_role).lower()
    r_role = required_role.value if isinstance(required_role, Role) else str(required_role).lower()

    user_level = _ROLE_HIERARCHY.get(u_role, -1)
    required_level = _ROLE_HIERARCHY.get(r_role, 99)
    return user_level >= required_level


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Security(security_bearer),
) -> dict[str, Any]:
    """FastAPI dependency: extract and verify Cognito Bearer token."""
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Bearer authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    try:
        user = verify_cognito_token(token)
        return user
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired authentication token: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_role(min_role: str | Role) -> Callable[..., Any]:
    """Dependency factory that ensures the authenticated user has at least min_role."""
    expected = min_role.value if isinstance(min_role, Role) else str(min_role).lower()

    async def _role_checker(
        current_user: dict[str, Any] = Depends(get_current_user),
    ) -> dict[str, Any]:
        user_role = current_user.get("role", Role.VIEWER.value)
        if not check_permission(user_role, expected):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: operation requires '{expected}' role (user has '{user_role}')",
            )
        return current_user

    return _role_checker


require_viewer = require_role(Role.VIEWER)
require_editor = require_role(Role.EDITOR)
require_owner = require_role(Role.OWNER)
