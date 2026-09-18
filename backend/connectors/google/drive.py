"""Google Drive connector implementation."""
from typing import Any, Dict, List

from backend.connectors.google.oauth import GoogleOAuthConnector
from backend.utils.errors import ConnectorError


class GoogleDriveConnector(GoogleOAuthConnector):
    """Google Drive specific connector."""

    async def execute(self, action: str, **kwargs) -> Any:
        """Execute Drive action."""
        await self.authenticate()
        await self.refresh_if_needed()

        if action == "list_files":
            return await self._list_files(**kwargs)
        elif action == "get_file_metadata":
            return await self._get_file_metadata(**kwargs)
        else:
            raise ConnectorError("google_drive", f"Unsupported action: {action}")

    async def _list_files(self, folder_id: str, query: str = "") -> List[Dict[str, Any]]:
        """List files in a drive folder."""
        # Production: Use googleapiclient.discovery.build('drive', 'v3', credentials=self._credentials)
        return [
            {"id": "mock_file_1", "name": "mock_report.pdf", "mimeType": "application/pdf"}
        ]

    async def _get_file_metadata(self, file_id: str) -> Dict[str, Any]:
        """Get metadata for a specific file."""
        return {"id": file_id, "name": "mock_file", "webViewLink": f"https://drive.google.com/mock/{file_id}"}
