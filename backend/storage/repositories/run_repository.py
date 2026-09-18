"""Run repository."""
from typing import Optional

from backend.models.run import Run
from backend.storage.dynamodb_client import DynamoDBClient


class RunRepository:
    """Repository for Run entity."""

    def __init__(self, dynamodb_client: DynamoDBClient):
        self.db = dynamodb_client

    def _make_pk(self, workflow_id: str) -> str:
        return f"WF#{workflow_id}"

    def _make_sk(self, run_id: str) -> str:
        return f"RUN#{run_id}"

    def create(self, run: Run) -> None:
        """Create new run."""
        item = run.model_dump()
        item["pk"] = self._make_pk(run.workflow_id)
        item["sk"] = self._make_sk(run.run_id)
        item["GSI1PK"] = f"ORG#{run.organization_id}"
        item["GSI1SK"] = f"RUN#{run.run_id}"
        self.db.put_item(item)

    def get(self, workflow_id: str, run_id: str) -> Optional[Run]:
        """Get run by ID."""
        item = self.db.get_item(self._make_pk(workflow_id), self._make_sk(run_id))
        if item:
            return Run(**item)
        return None

    def list_by_workflow(self, workflow_id: str, limit: Optional[int] = None) -> list[Run]:
        """List runs for a workflow."""
        items = self.db.query(
            pk=self._make_pk(workflow_id),
            sk_prefix="RUN#",
            limit=limit,
            scan_forward=False,  # Newest first
        )
        return [Run(**item) for item in items]

    def list_by_organization(self, organization_id: str, limit: Optional[int] = None) -> list[Run]:
        """List runs in organization."""
        items = self.db.query(
            pk=f"ORG#{organization_id}",
            sk_prefix="RUN#",
            index_name="GSI1",
            limit=limit,
            scan_forward=False,  # Newest first
        )
        return [Run(**item) for item in items]

    def update(self, run: Run) -> None:
        """Update existing run."""
        item = run.model_dump()
        item["pk"] = self._make_pk(run.workflow_id)
        item["sk"] = self._make_sk(run.run_id)
        item["GSI1PK"] = f"ORG#{run.organization_id}"
        item["GSI1SK"] = f"RUN#{run.run_id}"
        self.db.put_item(item)
