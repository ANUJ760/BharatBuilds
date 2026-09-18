"""Timeline repository."""
from typing import Optional

from backend.models.timeline import TimelineStep
from backend.storage.dynamodb_client import DynamoDBClient


class TimelineRepository:
    """Repository for TimelineStep entity."""

    def __init__(self, dynamodb_client: DynamoDBClient):
        self.db = dynamodb_client

    def _make_pk(self, run_id: str) -> str:
        return f"RUN#{run_id}"

    def _make_sk(self, step_id: str) -> str:
        return f"STEP#{step_id}"

    def create(self, step: TimelineStep) -> None:
        """Create new timeline step."""
        item = step.model_dump()
        item["pk"] = self._make_pk(step.run_id)
        item["sk"] = self._make_sk(step.step_id)
        self.db.put_item(item)

    def get(self, run_id: str, step_id: str) -> Optional[TimelineStep]:
        """Get timeline step by ID."""
        item = self.db.get_item(self._make_pk(run_id), self._make_sk(step_id))
        if item:
            return TimelineStep(**item)
        return None

    def list_by_run(self, run_id: str) -> list[TimelineStep]:
        """List all timeline steps for a run."""
        items = self.db.query(
            pk=self._make_pk(run_id),
            sk_prefix="STEP#",
            scan_forward=True,  # Oldest first to maintain chronology
        )
        return [TimelineStep(**item) for item in items]

    def update(self, step: TimelineStep) -> None:
        """Update existing timeline step."""
        item = step.model_dump()
        item["pk"] = self._make_pk(step.run_id)
        item["sk"] = self._make_sk(step.step_id)
        self.db.put_item(item)

    def batch_write(self, steps: list[TimelineStep]) -> None:
        """Batch write multiple timeline steps."""
        items = []
        for step in steps:
            item = step.model_dump()
            item["pk"] = self._make_pk(step.run_id)
            item["sk"] = self._make_sk(step.step_id)
            items.append(item)

        if items:
            self.db.batch_write(items)
