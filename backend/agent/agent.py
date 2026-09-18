"""Core Agent implementation interacting with Strands/Bedrock."""
from typing import Any, Dict, List, Optional
import structlog

from backend.models.workflow import WorkflowDefinition
from backend.authorization.context import AuthContext
from backend.tools.registry import ToolRegistry
from backend.agent.bedrock_client import BedrockClient
from backend.utils.errors import AgentExecutionError
from backend.storage.repositories.timeline_repository import TimelineRepository
from backend.models.timeline import TimelineStep, TimelineStepType, TimelineStepStatus
from backend.utils.ids import generate_step_id

logger = structlog.get_logger(__name__)


class MicroAgent:
    """The central agent responsible for reasoning and executing workflows."""

    def __init__(
        self,
        tool_registry: ToolRegistry,
        bedrock_client: BedrockClient,
        timeline_repo: TimelineRepository,
    ):
        self.tool_registry = tool_registry
        self.bedrock = bedrock_client
        self.timeline_repo = timeline_repo

    async def execute_workflow(
        self,
        workflow_id: str,
        run_id: str,
        workflow_def: WorkflowDefinition,
        auth_context: AuthContext,
        input_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute a validated structured workflow.

        This foundation demonstrates the interaction between the agent,
        the tool registry, authorization layer, and the timeline.
        """
        logger.info("agent_execution_started", workflow_id=workflow_id, run_id=run_id)

        # 1. Look up allowed tools based on the workflow and authorization
        # We pass allowed_tools as a set so the tool registry can filter authorized tools
        workflow_allowed_tools = set(workflow_def.allowed_tools)
        available_tools = self.tool_registry.get_allowed_tools(
            auth_context=auth_context,
            workflow_allowed_tools=workflow_allowed_tools
        )

        logger.info("agent_tools_authorized", count=len(available_tools))

        # Create initial timeline step (Reasoning block)
        step_id = generate_step_id()
        current_step = TimelineStep(
            step_id=step_id,
            workflow_id=workflow_id,
            run_id=run_id,
            organization_id=auth_context.organization_id,
            type=TimelineStepType.REASONING,
            status=TimelineStepStatus.RUNNING,
            input=input_data,
            plan=f"Executing workflow: {workflow_def.name}"
        )
        self.timeline_repo.create(current_step)

        # In a full implementation using Strands SDK, we'd initialize the loop here.
        # For this foundation, we simulate the agent moving through the predefined steps.

        results = {}
        parent_step_id = step_id

        try:
            for i, step_def in enumerate(workflow_def.steps):
                tool_name = step_def.tool

                # Check if tool is in the authorized list we fetched earlier
                if not any(t.name == tool_name for t in available_tools):
                    # Authorization Boundary Enforcement
                    raise AgentExecutionError(f"Tool {tool_name} not authorized or registered")

                # Create timeline step for tool execution
                tool_step_id = generate_step_id()
                tool_step = TimelineStep(
                    step_id=tool_step_id,
                    parent_step_id=parent_step_id,
                    workflow_id=workflow_id,
                    run_id=run_id,
                    organization_id=auth_context.organization_id,
                    type=TimelineStepType.TOOL_CALL,
                    status=TimelineStepStatus.RUNNING,
                    tool=tool_name,
                    tool_arguments=step_def.input or {}
                )
                self.timeline_repo.create(tool_step)

                # Execute tool using registry (which does policy engine checks underneath)
                tool_result = await self.tool_registry.execute(
                    name=tool_name,
                    arguments=step_def.input or {},
                    auth_context=auth_context,
                    workflow_allowed_tools=workflow_allowed_tools
                )

                # Store result
                results[f"step_{i}"] = tool_result

                # Update timeline
                tool_step.status = TimelineStepStatus.SUCCESS
                tool_step.output = {"result": tool_result}
                self.timeline_repo.update(tool_step)

                parent_step_id = tool_step_id

            # Finish execution
            current_step.status = TimelineStepStatus.SUCCESS
            current_step.output = {"final_results": results}
            self.timeline_repo.update(current_step)

            return {"status": "success", "data": results}

        except Exception as e:
            # Safely catch error and write to timeline
            logger.error("agent_execution_failed", error=str(e))
            current_step.status = TimelineStepStatus.ERROR
            current_step.error_message = str(e)
            self.timeline_repo.update(current_step)
            raise AgentExecutionError(f"Agent execution failed: {str(e)}")
