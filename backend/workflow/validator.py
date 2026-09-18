"""Workflow definition validator."""
from typing import Any, Dict, List

import jsonschema
import structlog

from backend.models.workflow import WorkflowDefinition
from backend.utils.errors import WorkflowValidationError
from backend.workflow.schema import WORKFLOW_DEFINITION_SCHEMA

logger = structlog.get_logger(__name__)


class WorkflowValidator:
    """Validates workflow definitions against the JSON schema and business rules."""

    def __init__(self):
        self.schema = WORKFLOW_DEFINITION_SCHEMA

    def validate_schema(self, definition: Dict[str, Any]) -> None:
        """Validate the raw workflow definition dict against the JSON schema."""
        try:
            jsonschema.validate(instance=definition, schema=self.schema)
        except jsonschema.ValidationError as e:
            logger.warning("workflow_schema_validation_failed", error=e.message)
            raise WorkflowValidationError(
                f"Workflow definition failed schema validation: {e.message}",
                details={"path": list(e.path), "validator": e.validator},
            )

    def validate_business_rules(self, definition: WorkflowDefinition) -> None:
        """Validate business rules on the typed WorkflowDefinition model."""
        errors: List[str] = []

        # Every step tool must be listed in allowed_tools
        allowed = set(definition.allowed_tools)
        for i, step in enumerate(definition.steps):
            if step.tool not in allowed:
                errors.append(
                    f"Step {i} references tool '{step.tool}' which is not in allowed_tools"
                )

        # Allowed tools must be non-empty for safety
        if not allowed:
            errors.append("allowed_tools must contain at least one tool")

        # Validate trigger schedule format for scheduled triggers
        if definition.trigger.type.value == "scheduled":
            if not definition.trigger.schedule:
                errors.append("Scheduled triggers require a 'schedule' cron expression")

        if errors:
            logger.warning("workflow_business_rules_failed", errors=errors)
            raise WorkflowValidationError(
                "Workflow definition failed business rule validation",
                details={"errors": errors},
            )

        logger.info("workflow_validated", name=definition.name, steps=len(definition.steps))

    def validate(self, definition: WorkflowDefinition) -> None:
        """Full validation: schema + business rules."""
        # Convert model to dict for schema validation
        definition_dict = definition.model_dump()
        self.validate_schema(definition_dict)
        self.validate_business_rules(definition)