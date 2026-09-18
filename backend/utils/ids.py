"""Utility functions for ID generation."""
import uuid
from typing import Optional


def generate_id(prefix: Optional[str] = None) -> str:
    """Generate a unique identifier with optional prefix.

    Args:
        prefix: Optional prefix for the ID (e.g., 'app', 'wf', 'run')

    Returns:
        Unique identifier string
    """
    unique_id = str(uuid.uuid4())
    if prefix:
        return f"{prefix}_{unique_id}"
    return unique_id


def generate_app_id() -> str:
    """Generate app identifier."""
    return generate_id("app")


def generate_workflow_id() -> str:
    """Generate workflow identifier."""
    return generate_id("wf")


def generate_run_id() -> str:
    """Generate run identifier."""
    return generate_id("run")


def generate_step_id() -> str:
    """Generate timeline step identifier."""
    return generate_id("step")


def generate_connection_id() -> str:
    """Generate connection identifier."""
    return generate_id("conn")


def generate_invite_id() -> str:
    """Generate invite identifier."""
    return generate_id("inv")


def generate_organization_id() -> str:
    """Generate organization identifier."""
    return generate_id("org")


def generate_user_id() -> str:
    """Generate user identifier."""
    return generate_id("user")
