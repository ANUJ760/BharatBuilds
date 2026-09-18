"""Amazon Bedrock client wrapper."""
import boto3


def get_bedrock_client():
    """Return a Bedrock Runtime client."""
    return boto3.client("bedrock-runtime")


async def invoke_model(prompt: str, system: str = "", model_id: str = "") -> str:
    """Invoke a Bedrock model and return the response text."""
    # TODO: implement model invocation
    pass
