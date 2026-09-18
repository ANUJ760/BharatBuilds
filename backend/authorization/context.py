"""Authorization Context for MicroAgent Cedar evaluation."""
from pydantic import BaseModel, Field
from typing import Optional, Any


class AuthContext(BaseModel):
    """Context information required for authorization decisions."""

    # Principal identifying attributes
    user_id: str = Field(..., description="ID of the user making the request")
    organization_id: str = Field(..., description="Organization ID of the requesting user")
    role: str = Field(..., description="Role of the user (e.g., owner, editor, viewer)")

    # Environment/Execution context
    workflow_id: Optional[str] = Field(None, description="ID of the workflow being executed")
    run_id: Optional[str] = Field(None, description="ID of the current run")

    # Resource context
    connection_id: Optional[str] = Field(None, description="Connection being used")

    def to_cedar_context(self) -> dict[str, Any]:
        """Convert to format expected by Cedar Python bindings context."""
        context = {
            "organization_id": self.organization_id,
            "role": self.role,
        }

        if self.workflow_id:
            context["workflow_id"] = self.workflow_id

        if self.run_id:
            context["run_id"] = self.run_id

        if self.connection_id:
            context["connection_id"] = self.connection_id

        return context
