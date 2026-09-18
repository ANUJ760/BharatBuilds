"""Create / list / get deployed apps."""
from fastapi import APIRouter

router = APIRouter(prefix="/apps", tags=["apps"])


@router.post("/")
async def create_app():
    # TODO: trigger agent pipeline
    pass


@router.get("/")
async def list_apps():
    # TODO: list user's deployed apps
    pass


@router.get("/{app_id}")
async def get_app(app_id: str):
    # TODO: get single app details
    pass
