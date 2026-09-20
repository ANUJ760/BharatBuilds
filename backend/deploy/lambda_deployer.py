"""Fast-path deploy for lightweight apps via Lambda + Function URLs.

Packages generated code, deploys/updates it to the Lambda function
created manually in the AWS console, and returns the live Function URL.
"""

from __future__ import annotations

import base64
import io
import logging
import zipfile

import boto3

logger = logging.getLogger(__name__)


def _get_client(region: str = "ap-south-1"):
    """Return a Lambda client."""
    return boto3.client("lambda", region_name=region)


def _package_code(code: str) -> bytes:
    """Package generated code into a zip archive for Lambda deployment.

    Creates a zip with a ``lambda_function.py`` entry that wraps the
    generated app code behind an API Gateway / Function URL compatible
    handler, and serves the HTML file.
    """
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        # The generated HTML code
        zf.writestr("index.html", code)
        # Lambda handler that serves the HTML
        handler_code = _generate_handler()
        zf.writestr("lambda_function.py", handler_code)
    buf.seek(0)
    return buf.read()


def _generate_handler() -> str:
    """Generate the Lambda handler that serves the generated app."""
    return '''\
"""Auto-generated Lambda handler for BharatBuilds deployed app."""

import json
import os
import traceback


def lambda_handler(event, context):
    """Handle Function URL / API Gateway requests."""
    try:
        # Read the generated HTML code
        with open("index.html", "r", encoding="utf-8") as f:
            html = f.read()

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "text/html"},
            "body": html,
        }
    except Exception as exc:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": "Internal server error",
                "detail": str(exc),
            }),
        }
'''


async def deploy_to_lambda(
    app_id: str,
    code: str,
    *,
    function_name: str = "",
    region: str = "ap-south-1",
) -> str:
    """Package and deploy app code to a Lambda function.

    Updates the existing Lambda function's code (created manually in
    the console per BUILD_GUIDE Section 1a). Returns the live
    Function URL.

    Parameters
    ----------
    app_id:
        The app's unique identifier (for logging).
    code:
        The generated Python source code.
    function_name:
        Lambda function name. Required.
    region:
        AWS region.

    Returns
    -------
    str
        The live Function URL where the app is accessible.

    Raises
    ------
    botocore.exceptions.ClientError
        On Lambda API errors.
    """
    client = _get_client(region=region)
    zip_bytes = _package_code(code)

    logger.info(
        "Deploying app %s to Lambda %s (zip size=%d bytes)",
        app_id,
        function_name,
        len(zip_bytes),
    )

    # Update the function code
    client.update_function_code(
        FunctionName=function_name,
        ZipFile=zip_bytes,
        Publish=True,
    )

    # Get or create the Function URL
    try:
        url_config = client.get_function_url_config(
            FunctionName=function_name,
        )
        function_url = url_config["FunctionUrl"]
    except client.exceptions.ResourceNotFoundException:
        url_response = client.create_function_url_config(
            FunctionName=function_name,
            AuthType="NONE",
        )
        function_url = url_response["FunctionUrl"]

    logger.info("App %s deployed at: %s", app_id, function_url)
    return function_url
