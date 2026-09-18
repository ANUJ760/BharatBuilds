"""S3 client for MicroAgent."""
import json
from typing import Optional

import boto3
import structlog
from botocore.exceptions import ClientError

from backend.config.settings import get_settings

logger = structlog.get_logger(__name__)


class S3Client:
    """S3 client wrapper for artifact storage."""

    def __init__(self):
        """Initialize S3 client."""
        settings = get_settings()

        session = boto3.Session()

        config = {
            "region_name": settings.aws_region,
        }

        if settings.s3_endpoint_url:
            config["endpoint_url"] = settings.s3_endpoint_url

        self.s3 = session.client("s3", **config)
        self.bucket_name = settings.s3_bucket_name

    def put_object(
        self,
        key: str,
        body: bytes,
        content_type: str = "application/octet-stream",
        metadata: Optional[dict[str, str]] = None,
    ) -> str:
        """Upload object to S3.

        Args:
            key: S3 object key
            body: Object content
            content_type: Content type
            metadata: Optional metadata

        Returns:
            S3 URI

        Raises:
            ClientError: If S3 operation fails
        """
        try:
            put_kwargs = {
                "Bucket": self.bucket_name,
                "Key": key,
                "Body": body,
                "ContentType": content_type,
            }

            if metadata:
                put_kwargs["Metadata"] = metadata

            self.s3.put_object(**put_kwargs)

            s3_uri = f"s3://{self.bucket_name}/{key}"
            logger.info("put_object_success", bucket=self.bucket_name, key=key, size=len(body))
            return s3_uri
        except ClientError as e:
            logger.error("put_object_failed", error=str(e), bucket=self.bucket_name, key=key)
            raise

    def get_object(self, key: str) -> bytes:
        """Download object from S3.

        Args:
            key: S3 object key

        Returns:
            Object content

        Raises:
            ClientError: If S3 operation fails
        """
        try:
            response = self.s3.get_object(Bucket=self.bucket_name, Key=key)
            body = response["Body"].read()
            logger.info("get_object_success", bucket=self.bucket_name, key=key, size=len(body))
            return body
        except ClientError as e:
            logger.error("get_object_failed", error=str(e), bucket=self.bucket_name, key=key)
            raise

    def delete_object(self, key: str) -> None:
        """Delete object from S3.

        Args:
            key: S3 object key

        Raises:
            ClientError: If S3 operation fails
        """
        try:
            self.s3.delete_object(Bucket=self.bucket_name, Key=key)
            logger.info("delete_object_success", bucket=self.bucket_name, key=key)
        except ClientError as e:
            logger.error("delete_object_failed", error=str(e), bucket=self.bucket_name, key=key)
            raise

    def object_exists(self, key: str) -> bool:
        """Check if object exists in S3.

        Args:
            key: S3 object key

        Returns:
            True if object exists, False otherwise
        """
        try:
            self.s3.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            logger.error("object_exists_failed", error=str(e), bucket=self.bucket_name, key=key)
            raise

    def generate_presigned_url(
        self,
        key: str,
        expiration: int = 3600,
        operation: str = "get_object",
    ) -> str:
        """Generate presigned URL for S3 object.

        Args:
            key: S3 object key
            expiration: URL expiration in seconds
            operation: S3 operation (get_object or put_object)

        Returns:
            Presigned URL

        Raises:
            ClientError: If S3 operation fails
        """
        try:
            url = self.s3.generate_presigned_url(
                operation,
                Params={"Bucket": self.bucket_name, "Key": key},
                ExpiresIn=expiration,
            )
            logger.info("generate_presigned_url_success", bucket=self.bucket_name, key=key, operation=operation)
            return url
        except ClientError as e:
            logger.error("generate_presigned_url_failed", error=str(e), bucket=self.bucket_name, key=key)
            raise

    def put_json(self, key: str, data: dict, metadata: Optional[dict[str, str]] = None) -> str:
        """Upload JSON object to S3.

        Args:
            key: S3 object key
            data: JSON-serializable data
            metadata: Optional metadata

        Returns:
            S3 URI

        Raises:
            ClientError: If S3 operation fails
        """
        json_bytes = json.dumps(data, indent=2).encode("utf-8")
        return self.put_object(key, json_bytes, content_type="application/json", metadata=metadata)

    def get_json(self, key: str) -> dict:
        """Download JSON object from S3.

        Args:
            key: S3 object key

        Returns:
            Parsed JSON data

        Raises:
            ClientError: If S3 operation fails
        """
        body = self.get_object(key)
        return json.loads(body.decode("utf-8"))
