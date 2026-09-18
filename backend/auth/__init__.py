"""Authentication layer."""
from backend.auth.cognito_client import CognitoClient
from backend.auth.roles import (
    UserRole,
    check_permission,
    require_permission,
    get_role_level,
    can_manage_users,
    can_edit_resources,
    can_view_resources,
)

__all__ = [
    "CognitoClient",
    "UserRole",
    "check_permission",
    "require_permission",
    "get_role_level",
    "can_manage_users",
    "can_edit_resources",
    "can_view_resources",
]