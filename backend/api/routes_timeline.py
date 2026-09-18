"""GET /apps/{id}/timeline, POST /revert/{step_id}."""
from fastapi import APIRouter

router = APIRouter(tags=["timeline"])


@router.get("/apps/{app_id}/timeline")
async def get_timeline(app_id: str):
    # TODO: fetch decision timeline nodes from DynamoDB
    pass


@router.post("/revert/{step_id}")
async def revert_to_step(step_id: str):
    # TODO: redeploy code snapshot from step
    pass
