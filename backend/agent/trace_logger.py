"""Writes every agent step to DynamoDB as a timeline node."""


async def log_step(app_id: str, step_data: dict) -> str:
    """
    Persist an agent step (plan, tool call, codegen, retry, deploy)
    to DynamoDB. Returns the step_id.
    """
    # TODO: write to DynamoDB with app_id PK and step_id SK
    pass
