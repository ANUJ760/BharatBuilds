"""Deploy generated app to AWS Fargate (ECS)."""


async def deploy_to_fargate(app_id: str, code: str) -> str:
    """
    Package and deploy app code to a Fargate container.
    Returns the live URL.
    """
    # TODO: build container image, push to ECR, update ECS service
    pass
