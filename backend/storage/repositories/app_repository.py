"""App repository."""
from typing import Optional

from backend.models.app import App
from backend.storage.dynamodb_client import DynamoDBClient
from backend.utils.timestamps import to_iso8601


class AppRepository:
    """Repository for App entity."""

    def __init__(self, dynamodb_client: DynamoDBClient):
        self.db = dynamodb_client

    def _make_pk(self, organization_id: str) -> str:
        return f"ORG#{organization_id}"

    def _make_sk(self, app_id: str) -> str:
        return f"APP#{app_id}"

    def create(self, app: App) -> None:
        """Create new app."""
        item = app.model_dump()
        item["pk"] = self._make_pk(app.organization_id)
        item["sk"] = self._make_sk(app.app_id)
        self.db.put_item(item)

    def get(self, organization_id: str, app_id: str) -> Optional[App]:
        """Get app by ID."""
        item = self.db.get_item(self._make_pk(organization_id), self._make_sk(app_id))
        if item:
            return App(**item)
        return None

    def list_by_organization(self, organization_id: str, limit: Optional[int] = None) -> list[App]:
        """List apps in organization."""
        items = self.db.query(
            pk=self._make_pk(organization_id),
            sk_prefix="APP#",
            limit=limit,
        )
        return [App(**item) for item in items]

    def update(self, app: App) -> None:
        """Update existing app."""
        item = app.model_dump()
        item["pk"] = self._make_pk(app.organization_id)
        item["sk"] = self._make_sk(app.app_id)
        self.db.put_item(item)

    def delete(self, organization_id: str, app_id: str) -> None:
        """Delete app."""
        self.db.delete_item(self._make_pk(organization_id), self._make_sk(app_id))
