"""Viewer / Editor role enforcement."""

ROLES = {"viewer", "editor", "owner"}


def check_permission(user_role: str, required_role: str) -> bool:
    """Check if user_role meets the required_role level."""
    hierarchy = {"viewer": 0, "editor": 1, "owner": 2}
    return hierarchy.get(user_role, -1) >= hierarchy.get(required_role, 99)
