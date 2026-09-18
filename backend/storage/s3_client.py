"""S3 client for generated app assets.

Handles uploading code bundles and static assets, and generating
pre-signed or plain URLs for retrieval.
"""

from __future__ import annotations

import boto3


def _get_client(region: str = "ap-south-1"):
    """Return a low-level S3 client."""
    return boto3.client("s3", region_name=region)


def upload_asset(
    bucket: str,
    key: str,
    body: str | bytes,
    *,
    content_type: str = "application/octet-stream",
    region: str = "ap-south-1",
) -> str:
    """Upload an asset to S3. Returns the full S3 URI (``s3://bucket/key``)."""
    client = _get_client(region=region)
    if isinstance(body, str):
        body = body.encode("utf-8")
    client.put_object(
        Bucket=bucket,
        Key=key,
        Body=body,
        ContentType=content_type,
    )
    return f"s3://{bucket}/{key}"


def get_asset(
    bucket: str,
    key: str,
    *,
    region: str = "ap-south-1",
) -> bytes:
    """Download an asset from S3. Returns the raw bytes."""
    client = _get_client(region=region)
    response = client.get_object(Bucket=bucket, Key=key)
    return response["Body"].read()


def get_asset_url(
    bucket: str,
    key: str,
    *,
    region: str = "ap-south-1",
    expires_in: int = 3600,
) -> str:
    """Generate a pre-signed URL for an S3 asset.

    Defaults to a 1-hour expiry.
    """
    client = _get_client(region=region)
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=expires_in,
    )


def delete_asset(
    bucket: str,
    key: str,
    *,
    region: str = "ap-south-1",
) -> None:
    """Delete an asset from S3."""
    client = _get_client(region=region)
    client.delete_object(Bucket=bucket, Key=key)
