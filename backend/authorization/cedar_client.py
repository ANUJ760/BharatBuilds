"""Cedar Client abstraction.

NOTE: Since cedar-py or typical AWS verified permissions might be used in production,
this provides the interface and a mock implementation for local development
if the C bindings are not available or configured.
"""
import json
import logging
from typing import Dict, Any

import structlog

logger = structlog.get_logger(__name__)


class CedarEvaluator:
    """Evaluates Cedar policies using a local Python engine (mock/fallback)
    or AWS Verified Permissions in production."""

    def __init__(self, policy_store_path: str = "policies/cedar"):
        self.policy_store_path = policy_store_path
        self._load_policies()

    def _load_policies(self):
        """Load policies from disk. Mock implementation."""
        # In a real environment, this would parse Cedar syntax via bindings
        # or load into AWS Verified Permissions
        pass

    def evaluate(
        self,
        principal: Dict[str, str],
        action: Dict[str, str],
        resource: Dict[str, str],
        context: Dict[str, Any],
    ) -> bool:
        """Evaluate a request against Cedar policies.

        Args:
            principal: e.g., {'entity_type': 'User', 'entity_id': 'user123'}
            action: e.g., {'entity_type': 'Action', 'entity_id': 'ReadDocument'}
            resource: e.g., {'entity_type': 'DriveFile', 'entity_id': 'file456'}
            context: Additional contextual attributes

        Returns:
            bool: True if allowed, False if denied
        """
        # --- MOCK CEDAR EVALUATION LOGIC FOR FOUNDATION ---
        # A real implementation would call cedar_py.is_authorized(...)

        logger.info(
            "cedar_evaluate_mock",
            principal=principal["entity_id"],
            action=action["entity_id"],
            resource=resource["entity_id"],
        )

        user_org = context.get("organization_id")
        resource_org = resource.get("organization_id")  # Injected by policy engine

        # Cross-tenant check (fundamental invariant)
        if resource_org and user_org != resource_org:
            logger.warning("cedar_deny_cross_tenant", user_org=user_org, resource_org=resource_org)
            return False

        # Demo policy mock: Allow ReadDocument if action matches
        if action.get("entity_id") == "ReadDocument" or action.get("entity_id") == "ListDocuments":
            return True

        if action.get("entity_id") == "ExecuteTool":
            # For tools, we'd check if the tool is in the allowed list for the workflow
            return True

        # Default deny
        return False
