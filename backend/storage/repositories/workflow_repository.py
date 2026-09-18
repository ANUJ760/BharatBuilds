"""Workflow repository."""
from typing import Optional

from backend.models.workflow import Workflow
from backend.storage.dynamodb_client import DynamoDBClient


class WorkflowRepository:
    """Repository for Workflow entity."""

    def __init__(self, dynamodb_client: DynamoDBClient):
        self.db = dynamodb_client

    def _make_pk(self, organization_id: str) -> str:
        return f"ORG#{organization_id}"

    def _make_sk(self, workflow_id: str) -> str:
        return f"WF#{workflow_id}"

    def create(self, workflow: Workflow) -> None:
        """Create new workflow."""
        item = workflow.model_dump()
        item["pk"] = self._make_pk(workflow.organization_id)
        item["sk"] = self._make_sk(workflow.workflow_id)
        self.db.put_item(item)

    def get(self, organization_id: str, workflow_id: str) -> Optional[Workflow]:
        """Get workflow by ID."""
        item = self.db.get_item(self._make_pk(organization_id), self._make_sk(workflow_id))
        if item:
            return Workflow(**item)
        return None

    def list_by_organization(self, organization_id: str, limit: Optional[int] = None) -> list[Workflow]:
        """List workflows in organization."""
        items = self.db.query(
            pk=self._make_pk(organization_id),
            sk_prefix="WF#",
            limit=limit,
        )
        return [Workflow(**item) for item in items]

    def update(self, workflow: Workflow) -> None:
        """Update existing workflow."""
        item = workflow.model_dump()
        item["pk"] = self._make_pk(workflow.organization_id)
        item["sk"] = self._make_sk(workflow.workflow_id)
        self.db.put_item(item)

    def delete(self, organization_id: str, workflow_id: str) -> None:
        """Delete workflow."""
        self.db.delete_item(self._make_pk(organization_id), self._make_sk(workflow_id))
