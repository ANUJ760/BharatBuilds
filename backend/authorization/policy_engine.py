"""Policy Engine for the Authorization layer."""
import structlog
from typing import Any, Optional

from backend.authorization.context import AuthContext
from backend.authorization.cedar_client import CedarEvaluator
from backend.utils.errors import ResourceAccessDeniedError

logger = structlog.get_logger(__name__)


class PolicyEngine:
    """Core authorization policy engine."""

    def __init__(self):
        self.evaluator = CedarEvaluator()

    def is_authorized(
        self,
        auth_context: AuthContext,
        action: str,
        resource_type: str,
        resource_id: str,
        resource_attributes: Optional[dict[str, Any]] = None,
    ) -> bool:
        """Check if a principal is allowed to perform an action on a resource.

        Args:
            auth_context: The authorization context (user, org, etc.)
            action: The action to perform (e.g., 'ReadDocument', 'ExecuteTool')
            resource_type: The type of resource (e.g., 'DriveFile', 'Tool')
            resource_id: The specific resource ID
            resource_attributes: Additional attributes of the resource (e.g., its organization_id)

        Returns:
            bool: True if authorized, False otherwise
        """
        principal_entity = {
            "entity_type": "User",
            "entity_id": auth_context.user_id,
        }

        action_entity = {
            "entity_type": "Action",
            "entity_id": action,
        }

        resource_entity = {
            "entity_type": resource_type,
            "entity_id": resource_id,
        }

        # Embed resource attributes if provided
        if resource_attributes:
            resource_entity.update(resource_attributes)

        is_allowed = self.evaluator.evaluate(
            principal=principal_entity,
            action=action_entity,
            resource=resource_entity,
            context=auth_context.to_cedar_context(),
        )

        logger.info(
            "authorization_decision",
            allowed=is_allowed,
            user=auth_context.user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            workflow=auth_context.workflow_id,
        )

        return is_allowed

    def authorize_or_raise(
        self,
        auth_context: AuthContext,
        action: str,
        resource_type: str,
        resource_id: str,
        resource_attributes: Optional[dict[str, Any]] = None,
    ) -> None:
        """Check authorization and raise exception if denied."""
        if not self.is_authorized(auth_context, action, resource_type, resource_id, resource_attributes):
            raise ResourceAccessDeniedError(
                resource=f"{resource_type}::{resource_id}",
                action=action,
            )
