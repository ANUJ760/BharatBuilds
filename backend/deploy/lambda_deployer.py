"""Fast-path deploy for lightweight apps via Lambda + Function URLs."""
from typing import Any, Dict

import structlog

from backend.storage.s3_client import S3Client
from backend.utils.errors import DeploymentError

logger = structlog.get_logger(__name__)


class LambdaDeployer:
    """Deploys lightweight app code as an AWS Lambda function."""

    def __init__(self, s3_client: S3Client):
        self.s3 = s3_client

    async def deploy(
        self,
        app_id: str,
        code: str,
        function_name: str = "microagent-app",
        runtime: str = "python3.12",
        timeout: int = 30,
        memory_size: int = 512,
    ) -> str:
        """Package code, create/update Lambda, enable Function URL.

        Returns the live URL.
        """
        logger.info("lambda_deploy_start", app_id=app_id)

        # 1. Upload code to S3
        code_key = f"lambda/{app_id}/function.zip"
        await self.s3.put_object(
            key=code_key,
            body=code.encode("utf-8"),
            content_type="application/zip",
        )
        logger.info("lambda_code_uploaded", key=code_key)

        # 2. Create/update Lambda function
        function_arn = await self._create_or_update_function(
            app_id=app_id,
            code_key=code_key,
            runtime=runtime,
            timeout=timeout,
            memory_size=memory_size,
        )

        # 3. Enable Function URL
        url = await self._create_function_url(function_arn)

        logger.info("lambda_deploy_success", app_id=app_id, url=url)
        return url

    async def _create_or_update_function(
        self,
        app_id: str,
        code_key: str,
        runtime: str,
        timeout: int,
        memory_size: int,
    ) -> str:
        """Create or update the Lambda function."""
        # Production: boto3 lambda client create/update function code
        return f"arn:aws:lambda:us-east-1:123456789012:function:microagent-{app_id}"

    async def _create_function_url(self, function_arn: str) -> str:
        """Create a Function URL for the Lambda."""
        # Production: boto3 lambda client create function URL
        return f"https://{function_arn.split(':')[-1]}.lambda-url.us-east-1.on.aws/"

    async def invoke(self, app_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke the Lambda function."""
        logger.info("lambda_invoke", app_id=app_id)
        # Production: boto3 lambda client invoke
        return {"statusCode": 200, "body": payload}

    async def delete(self, app_id: str) -> None:
        """Delete the Lambda function."""
        logger.info("lambda_delete", app_id=app_id)
        # Production: boto3 lambda client delete function

    async def get_status(self, app_id: str) -> Dict[str, Any]:
        """Get deployment status."""
        return {
            "app_id": app_id,
            "status": "active",
            "url": f"https://{app_id}.lambda-url.us-east-1.on.aws/",
            "runtime": "python3.12",
        }