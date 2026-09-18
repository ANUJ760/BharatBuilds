"""Deploy-related endpoints."""
from fastapi import APIRouter

router = APIRouter(prefix="/deploy", tags=["deploy"])


@router.post("/{app_id}")
async def deploy_app(app_id: str):
    # TODO: trigger deploy pipeline
    pass


@router.get("/{app_id}/status")
async def deploy_status(app_id: str):
    # TODO: return deploy status
    pass
