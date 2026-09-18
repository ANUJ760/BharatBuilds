"""Custom error classes for MicroAgent backend."""
from typing import Any, Optional


class MicroAgentError(Exception):
    """Base exception for MicroAgent errors."""

    def __init__(self, message: str, code: str, details: Optional[dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}


class ResourceNotFoundError(MicroAgentError):
    """Resource not found."""

    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            message=f"{resource_type} with id {resource_id} not found",
            code="RESOURCE_NOT_FOUND",
            details={"resource_type": resource_type, "resource_id": resource_id},
        )


class UnauthorizedError(MicroAgentError):
    """Unauthorized access attempt."""

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message=message, code="UNAUTHORIZED")


class ForbiddenError(MicroAgentError):
    """Forbidden action."""

    def __init__(self, message: str = "Access denied"):
        super().__init__(message=message, code="FORBIDDEN")


class ResourceAccessDeniedError(MicroAgentError):
    """Resource access denied by authorization policy."""

    def __init__(self, resource: str, action: str):
        super().__init__(
            message=f"Access denied for action '{action}' on resource '{resource}'",
            code="RESOURCE_ACCESS_DENIED",
            details={"resource": resource, "action": action},
        )


class ValidationError(MicroAgentError):
    """Request validation error."""

    def __init__(self, message: str, field: Optional[str] = None):
        details = {"field": field} if field else {}
        super().__init__(message=message, code="VALIDATION_ERROR", details=details)


class WorkflowValidationError(MicroAgentError):
    """Workflow definition validation error."""

    def __init__(self, message: str):
        super().__init__(message=message, code="WORKFLOW_VALIDATION_ERROR")


class ToolNotFoundError(MicroAgentError):
    """Tool not found in registry."""

    def __init__(self, tool_name: str):
        super().__init__(
            message=f"Tool '{tool_name}' not found",
            code="TOOL_NOT_FOUND",
            details={"tool_name": tool_name},
        )


class ToolNotAllowedError(MicroAgentError):
    """Tool not allowed in workflow."""

    def __init__(self, tool_name: str, workflow_id: str):
        super().__init__(
            message=f"Tool '{tool_name}' is not allowed in workflow {workflow_id}",
            code="TOOL_NOT_ALLOWED",
            details={"tool_name": tool_name, "workflow_id": workflow_id},
        )


class AgentExecutionError(MicroAgentError):
    """Agent execution failed."""

    def __init__(self, message: str, agent_error: Optional[str] = None):
        super().__init__(
            message=message,
            code="AGENT_EXECUTION_ERROR",
            details={"agent_error": agent_error} if agent_error else {},
        )


class ConnectorError(MicroAgentError):
    """External connector error."""

    def __init__(self, provider: str, message: str):
        super().__init__(
            message=f"Connector error ({provider}): {message}",
            code="CONNECTOR_ERROR",
            details={"provider": provider},
        )


class ConnectionExpiredError(MicroAgentError):
    """Connection credentials expired."""

    def __init__(self, connection_id: str):
        super().__init__(
            message=f"Connection {connection_id} has expired",
            code="CONNECTION_EXPIRED",
            details={"connection_id": connection_id},
        )


class DeploymentError(MicroAgentError):
    """Deployment failed."""

    def __init__(self, message: str):
        super().__init__(message=message, code="DEPLOYMENT_ERROR")


class WorkflowTimeoutError(MicroAgentError):
    """Workflow execution timeout."""

    def __init__(self, workflow_id: str, timeout_seconds: int):
        super().__init__(
            message=f"Workflow {workflow_id} timed out after {timeout_seconds}s",
            code="WORKFLOW_TIMEOUT",
            details={"workflow_id": workflow_id, "timeout_seconds": timeout_seconds},
        )


class MaxStepsExceededError(MicroAgentError):
    """Maximum workflow steps exceeded."""

    def __init__(self, workflow_id: str, max_steps: int):
        super().__init__(
            message=f"Workflow {workflow_id} exceeded maximum steps ({max_steps})",
            code="MAX_STEPS_EXCEEDED",
            details={"workflow_id": workflow_id, "max_steps": max_steps},
        )


class ApprovalRequiredError(MicroAgentError):
    """Action requires human approval."""

    def __init__(self, action_name: str, run_id: str):
        super().__init__(
            message=f"Action '{action_name}' requires approval",
            code="APPROVAL_REQUIRED",
            details={"action_name": action_name, "run_id": run_id},
        )
