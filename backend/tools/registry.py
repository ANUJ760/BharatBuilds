"""Tool registry for maintaining execution boundaries."""
import inspect
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Set

import structlog

from backend.authorization.context import AuthContext
from backend.authorization.policy_engine import PolicyEngine
from backend.utils.errors import ToolNotAllowedError, ToolNotFoundError

logger = structlog.get_logger(__name__)


@dataclass
class ToolMetadata:
    """Metadata for a registered tool."""

    name: str
    description: str
    func: Callable
    risk_level: str  # e.g., 'READ', 'WRITE', 'EXECUTE'
    requires_approval: bool
    resources: List[str]  # e.g., ['employee_documents', 'employee_sheet']
    parameters_schema: Dict[str, Any]  # JSON schema of parameters


class ToolRegistry:
    """Central registry for all agent tools."""

    def __init__(self, policy_engine: PolicyEngine):
        self._tools: Dict[str, ToolMetadata] = {}
        self.policy_engine = policy_engine

    def register(
        self,
        name: str,
        description: str,
        func: Callable,
        risk_level: str = "READ",
        requires_approval: bool = False,
        resources: Optional[List[str]] = None,
        parameters_schema: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Register a new tool."""
        if name in self._tools:
            logger.warning("tool_registry_overwrite", tool_name=name)

        if parameters_schema is None:
            parameters_schema = self._generate_schema_from_func(func)

        self._tools[name] = ToolMetadata(
            name=name,
            description=description,
            func=func,
            risk_level=risk_level,
            requires_approval=requires_approval,
            resources=resources or [],
            parameters_schema=parameters_schema,
        )
        logger.info("tool_registered", tool_name=name, risk_level=risk_level)

    def _generate_schema_from_func(self, func: Callable) -> Dict[str, Any]:
        """Generate JSON schema from function signature using inspect."""
        sig = inspect.signature(func)
        properties = {}
        required = []

        for param_name, param in sig.parameters.items():
            if param_name in ("auth_context", "context", "self"):
                continue

            properties[param_name] = {"type": "string"}  # Default abstract type

            if param.default == inspect.Parameter.empty:
                required.append(param_name)

        schema = {
            "type": "object",
            "properties": properties,
        }

        if required:
            schema["required"] = required

        return schema

    def get_tool(self, name: str) -> ToolMetadata:
        """Get a registered tool."""
        if name not in self._tools:
            raise ToolNotFoundError(name)
        return self._tools[name]

    def get_allowed_tools(
        self,
        auth_context: AuthContext,
        workflow_allowed_tools: Set[str],
    ) -> List[ToolMetadata]:
        """Get tools allowed for the current context and workflow."""
        allowed = []
        for name in workflow_allowed_tools:
            if name in self._tools:
                tool = self._tools[name]

                # Check if principal is authorized to ExecuteTool
                resource_attributes = {
                    "organization_id": auth_context.organization_id,
                    "risk_level": tool.risk_level,
                    "workflow_id": auth_context.workflow_id
                }

                if self.policy_engine.is_authorized(
                    auth_context=auth_context,
                    action="ExecuteTool",
                    resource_type="Tool",
                    resource_id=name,
                    resource_attributes=resource_attributes,
                ):
                    allowed.append(tool)

        return allowed

    async def execute(
        self,
        name: str,
        arguments: Dict[str, Any],
        auth_context: AuthContext,
        workflow_allowed_tools: Set[str],
    ) -> Any:
        """Execute a tool after performing authorization."""
        if name not in workflow_allowed_tools:
            raise ToolNotAllowedError(name, auth_context.workflow_id or "unknown")

        tool = self.get_tool(name)

        # 1. Authorize Tool Execution
        resource_attributes = {
            "organization_id": auth_context.organization_id,
            "risk_level": tool.risk_level,
        }

        self.policy_engine.authorize_or_raise(
            auth_context=auth_context,
            action="ExecuteTool",
            resource_type="Tool",
            resource_id=name,
            resource_attributes=resource_attributes,
        )

        # 2. Authorize Resource Access (if tool touches specific resources)
        for resource in tool.resources:
            self.policy_engine.authorize_or_raise(
                auth_context=auth_context,
                action=f"AccessResource_{tool.risk_level}",
                resource_type="WorkflowResource",
                resource_id=resource,
                resource_attributes={"organization_id": auth_context.organization_id},
            )

        logger.info(
            "executing_tool",
            tool=name,
            user=auth_context.user_id,
            workflow=auth_context.workflow_id
        )

        # In a real implementation this would inject the auth_context if the function requires it
        if inspect.iscoroutinefunction(tool.func):
            return await tool.func(**arguments)
        else:
            return tool.func(**arguments)
