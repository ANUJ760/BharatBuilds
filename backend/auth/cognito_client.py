"""Amazon Cognito client for auth operations."""
import boto3


def get_cognito_client():
    """Return a Cognito Identity Provider client."""
    return boto3.client("cognito-idp")


async def create_user(email: str) -> dict:
    """Create a Cognito user for app sharing (magic link / OTP)."""
    # TODO: implement user creation
    pass
