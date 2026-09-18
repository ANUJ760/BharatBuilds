"""Workflow executor: orchestrates the agent execution of a workflow."""
from typing import Any, Dict

import structlog

from backend.agent.agent import MicroAgent
from backend.authorization.context import AuthContext
from backend.models.run import Run
from backend.models.workflow import WorkflowDefinition
from backend.storage.repositories.run_repository import RunRepository
from backend.storage.repositories.timeline_repository import TimelineRepository
from backend.tools.registry import ToolRegistry
from backend.utils.errors import AgentExecutionError
from backend.utils.ids import generate_run_id
from backend.utils.timestamps import utcnow

logger = structlog.get_logger(__name__)


class WorkflowExecutor:
    """Executes a validated workflow using the MicroAgent."""

    def __init__(
        self,
        agent: MicroAgent,
        run_repo: RunRepository,
        timeline_repo: TimelineRepository,
        tool_registry: ToolRegistry,
    ):
        self.agent = agent
        self.run_repo = run_repo
        self.timeline_repo = timeline_repo
        self.tool_registry = tool_registry

    async def execute(
        self,
        workflow_id: str,
        workflow_def: WorkflowDefinition,
        auth_context: AuthContext,
        input_data: Dict[str, Any],
    ) -> Run:
        """Execute a workflow and return the resulting Run entity."""
        run_id = generate_run_id()
        logger.info("workflow_executor_start", workflow_id=workflow_id, run_id=run_id)

        # Create the Run record
        run = Run(
            run_id=run_id,
            workflow_id=workflow_id,
            organization_id=auth_context.organization_id,
            triggered_by=auth_context.user_id,
            status="pending",
            input_data=input_data,
            started_at=utcnow(),
        )
        self.run_repo.create(run)

        # Update status to running
        run.status = "running"
        self.run_repo.update(run)

        try:
            result = await self.agent.execute_workflow(
                workflow_id=workflow_id,
                run_id=run_id,
                workflow_def=workflow_def,
                auth_context=auth_context,
                input_data=input_data,
            )

            run.status = "success"
            run.result = result
            run.completed_at = utcnow()
            self.run_repo.update(run)

            logger.info("workflow_executor_success", run_id=run_id)
            return run

        except AgentExecutionError as e:
            logger.error("workflow_executor_failed", run_id=run_id, error=str(e))
            run.status = "failed"
            run.error_message = str(e)
            run.completed_at = utcnow()
            self.run_repo.update(run)
            raise
        except Exception as e:
            logger.error("workflow_executor_unexpected_error", run_id=run_id, error=str(e))
            run.status = "failed"
            run.error_message = f"Unexpected error: {str(e)}"
            run.completed_at = utcnow()
            self.run_repo.update(run)
            raise