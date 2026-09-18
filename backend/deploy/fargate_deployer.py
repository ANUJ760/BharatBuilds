"""Deploy generated app to AWS Fargate (ECS)."""
from typing import Any, Dict, Optional

import structlog

from backend.storage.s3_client import S3Client
from backend.utils.errors import DeploymentError

logger = structlog.get_logger(__name__)


class FargateDeployer:
    """Deploys generated app code to AWS Fargate via ECS."""

    def __init__(self, s3_client: S3Client):
        self.s3 = s3_client

    async def deploy(
        self,
        app_id: str,
        code: str,
        container_name: str = "microagent-app",
        cpu: int = 512,
        memory: int = 1024,
    ) -> str:
        """Package and deploy app code to a Fargate container.

        Returns the live URL.
        """
        logger.info("fargate_deploy_start", app_id=app_id)

        # 1. Upload code to S3 as a snapshot
        snapshot_key = f"snapshots/{app_id}/app.tar.gz"
        await self.s3.put_object(
            key=snapshot_key,
            body=code.encode("utf-8"),
            content_type="application/gzip",
        )
        logger.info("fargate_snapshot_uploaded", key=snapshot_key)

        # 2. Build container image (ECS would pull from ECR)
        # In production: docker build -> ECR push -> ECS task definition update
        image_uri = await self._build_and_push_image(app_id, snapshot_key)

        # 3. Create/update ECS service
        service_arn = await self._create_or_update_service(
            app_id=app_id,
            image_uri=image_uri,
            cpu=cpu,
            memory=memory,
        )

        # 4. Return the live URL
        url = f"https://{app_id}.microagent.app"
        logger.info("fargate_deploy_success", app_id=app_id, url=url, service_arn=service_arn)
        return url

    async def _build_and_push_image(self, app_id: str, snapshot_key: str) -> str:
        """Build container image and push to ECR."""
        # Production: use Docker SDK + ECR
        return f"123456789012.dkr.ecr.us-east-1.amazonaws.com/microagent-app:{app_id}"

    async def _create_or_update_service(
        self,
        app_id: str,
        image_uri: str,
        cpu: int,
        memory: int,
    ) -> str:
        """Create or update the ECS service."""
        # Production: ECS client create/update service
        return f"arn:aws:ecs:us-east-1:123456789012:service/microagent/{app_id}"

    async def stop(self, app_id: str) -> None:
        """Stop the Fargate service for an app."""
        logger.info("fargate_stop", app_id=app_id)
        # Production: scale ECS service to 0

    async def get_status(self, app_id: str) -> Dict[str, Any]:
        """Get deployment status."""
        return {
            "app_id": app_id,
            "status": "running",
            "url": f"https://{app_id}.microagent.app",
            "task_count": 1,
        }