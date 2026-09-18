"""Decision Timeline service."""
from typing import List, Optional

import structlog

from backend.models.timeline import (
    TimelineStep,
    TimelineStepType,
    TimelineStepStatus,
)
from backend.storage.repositories.timeline_repository import TimelineRepository

logger = structlog.get_logger(__name__)


class TimelineService:
    """Service for managing the Decision Timeline tree."""

    def __init__(self, timeline_repo: TimelineRepository):
        self.repo = timeline_repo

    def create_step(
        self,
        run_id: str,
        workflow_id: str,
        organization_id: str,
        step_type: TimelineStepType,
        parent_step_id: Optional[str] = None,
        status: TimelineStepStatus = TimelineStepStatus.PENDING,
        **kwargs,
    ) -> TimelineStep:
        """Create a new timeline step."""
        from backend.utils.ids import generate_step_id

        step = TimelineStep(
            step_id=generate_step_id(),
            run_id=run_id,
            workflow_id=workflow_id,
            organization_id=organization_id,
            parent_step_id=parent_step_id,
            type=step_type,
            status=status,
            **kwargs,
        )
        self.repo.create(step)
        logger.info("timeline_step_created", step_id=step.step_id, type=step_type.value)
        return step

    def update_step(self, step: TimelineStep) -> None:
        """Update an existing timeline step."""
        self.repo.update(step)
        logger.info("timeline_step_updated", step_id=step.step_id, status=step.status.value)

    def get_step(self, run_id: str, step_id: str) -> Optional[TimelineStep]:
        """Get a single timeline step."""
        return self.repo.get(run_id, step_id)

    def list_by_run(self, run_id: str) -> List[TimelineStep]:
        """List all steps for a run in chronological order."""
        steps = self.repo.list_by_run(run_id)
        logger.info("timeline_listed", run_id=run_id, count=len(steps))
        return steps

    def build_tree(self, run_id: str) -> dict:
        """Build a tree representation of the timeline for a run.

        Returns a dict with root steps and nested children.
        """
        steps = self.list_by_run(run_id)
        step_map = {s.step_id: s for s in steps}

        # Attach children to parents
        for step in steps:
            step.children = []
            if step.parent_step_id and step.parent_step_id in step_map:
                step_map[step.parent_step_id].children.append(step)

        # Roots are steps without a parent
        roots = [s for s in steps if not s.parent_step_id]

        return {
            "run_id": run_id,
            "roots": [self._serialize_step(r) for r in roots],
            "total_steps": len(steps),
        }

    @staticmethod
    def _serialize_step(step: TimelineStep) -> dict:
        """Serialize a step and its children recursively."""
        data = step.model_dump()
        children = getattr(step, "children", [])
        data["children"] = [TimelineService._serialize_step(c) for c in children]
        return data