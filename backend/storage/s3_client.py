"""S3 client for generated app assets."""
import boto3


def get_s3_client():
    """Return an S3 client."""
    return boto3.client("s3")


async def upload_app_assets(app_id: str, assets: dict) -> str:
    """Upload generated app assets to S3. Returns the S3 prefix."""
    # TODO: implement asset upload
    pass
