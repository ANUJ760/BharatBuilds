"""Invites, roles for sharing apps."""
from fastapi import APIRouter

router = APIRouter(prefix="/share", tags=["share"])


@router.post("/{app_id}/invite")
async def invite_user(app_id: str):
    # TODO: send invite via SES, create Cognito user if needed
    pass
