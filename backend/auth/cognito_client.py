"""Amazon Cognito client for auth operations."""
from typing import Any, Dict, Optional

import boto3
import structlog

from backend.config.settings import get_settings

logger = structlog.get_logger(__name__)


class CognitoClient:
    """Client for Cognito User Pool operations."""

    def __init__(self):
        self.settings = get_settings()
        self.client = boto3.client(
            "cognito-idp",
            region_name=self.settings.aws_region,
        )
        self.user_pool_id = self.settings.cognito_user_pool_id

    def create_user(
        self,
        email: str,
        user_attributes: Optional[Dict[str, str]] = None,
        temporary_password: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a Cognito user for app sharing (magic link / OTP)."""
        logger.info("cognito_create_user", email=email)

        attributes = [{"Name": "email", "Value": email}]
        if user_attributes:
            for key, value in user_attributes.items():
                attributes.append({"Name": key, "Value": str(value)})

        response = self.client.admin_create_user(
            UserPoolId=self.user_pool_id,
            Username=email,
            UserAttributes=attributes,
            TemporaryPassword=temporary_password or "Temp@1234!",
            MessageAction="SUPPRESS",
        )

        logger.info("cognito_create_user_success", user_id=response.get("User", {}).get("Username"))
        return response

    def initiate_auth(
        self,
        email: str,
        password: str,
    ) -> Dict[str, Any]:
        """Initiate authentication flow (USER_PASSWORD_AUTH)."""
        logger.info("cognito_initiate_auth", email=email)

        response = self.client.initiate_auth(
            ClientId=self.settings.cognito_client_id,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": email,
                "PASSWORD": password,
            },
        )

        logger.info("cognito_initiate_auth_success")
        return response

    def initiate_signup(
        self,
        email: str,
        password: str,
        user_attributes: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Initiate sign up (sends confirmation code)."""
        logger.info("cognito_initiate_signup", email=email)

        user_attributes = user_attributes or {}
        attributes = [{"Name": "email", "Value": email}]
        for key, value in user_attributes.items():
            attributes.append({"Name": key, "Value": str(value)})

        response = self.client.sign_up(
            ClientId=self.settings.cognito_client_id,
            Username=email,
            Password=password,
            UserAttributes=attributes,
        )

        logger.info("cognito_initiate_signup_success")
        return response

    def confirm_signup(
        self,
        email: str,
        confirmation_code: str,
    ) -> Dict[str, Any]:
        """Confirm sign up with the verification code."""
        logger.info("cognito_confirm_signup", email=email)

        response = self.client.confirm_sign_up(
            ClientId=self.settings.cognito_client_id,
            Username=email,
            ConfirmationCode=confirmation_code,
        )

        logger.info("cognito_confirm_signup_success")
        return response

    def admin_set_user_password(
        self,
        email: str,
        new_password: str,
        permanent: bool = True,
    ) -> Dict[str, Any]:
        """Set a user's password (admin operation)."""
        logger.info("cognito_admin_set_password", email=email)

        response = self.client.admin_set_user_password(
            UserPoolId=self.user_pool_id,
            Username=email,
            Password=new_password,
            Permanent=permanent,
        )

        logger.info("cognito_admin_set_password_success")
        return response

    def get_user(self, access_token: str) -> Dict[str, Any]:
        """Get user info using an access token."""
        logger.info("cognito_get_user")

        response = self.client.get_user(AccessToken=access_token)
        return response

    def admin_get_user(self, email: str) -> Dict[str, Any]:
        """Get user by email (admin operation)."""
        logger.info("cognito_admin_get_user", email=email)

        response = self.client.admin_get_user(
            UserPoolId=self.user_pool_id,
            Username=email,
        )
        return response

    def list_users(self) -> Dict[str, Any]:
        """List all users in the pool."""
        logger.info("cognito_list_users")

        response = self.client.list_users(UserPoolId=self.user_pool_id)
        return response

    def admin_delete_user(self, email: str) -> Dict[str, Any]:
        """Delete a user (admin operation)."""
        logger.info("cognito_admin_delete_user", email=email)

        response = self.client.admin_delete_user(
            UserPoolId=self.user_pool_id,
            Username=email,
        )
        return response