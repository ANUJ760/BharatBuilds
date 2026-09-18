"""Base connector abstractions."""
from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseConnector(ABC):
    """Base class for all external resource connectors."""

    def __init__(self, connection_id: str, credential_reference: str):
        self.connection_id = connection_id
        self.credential_reference = credential_reference
        self._credentials = None

    @abstractmethod
    async def authenticate(self) -> None:
        """Authenticate with the external service using credentials."""
        pass

    @abstractmethod
    async def refresh_if_needed(self) -> None:
        """Refresh credentials if they are expired."""
        pass

    @abstractmethod
    async def validate_access(self, resource_id: str, required_scopes: list[str]) -> bool:
        """Validate if the connection has access to a specific resource."""
        pass

    @abstractmethod
    async def execute(self, action: str, **kwargs) -> Any:
        """Execute a specific action on the connector."""
        pass

    async def _fetch_credentials(self) -> Dict[str, Any]:
        """Fetch credentials securely from AWS Secrets Manager or DynamoDB.

        MOCK implementation for foundation.
        """
        # In production, use boto3 SecretsManager based on self.credential_reference
        return {
            "token": f"mock_token_for_{self.connection_id}",
            "refresh_token": "mock_refresh",
            "client_id": "mock_client",
            "client_secret": "mock_secret"
        }
