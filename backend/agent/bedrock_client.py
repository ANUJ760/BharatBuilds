"""Bedrock client wrapper."""
import json
from typing import Any, Dict, List, Optional

import boto3
import structlog
from botocore.exceptions import ClientError

from backend.config.settings import get_settings

logger = structlog.get_logger(__name__)


class BedrockClient:
    """Wrapper for Amazon Bedrock converse API."""

    def __init__(self):
        self.settings = get_settings()
        self.client = boto3.client("bedrock-runtime", region_name=self.settings.bedrock_region)
        self.model_id = self.settings.bedrock_model_id

    def converse(
        self,
        messages: List[Dict[str, Any]],
        system_prompts: Optional[List[Dict[str, str]]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Call Bedrock converse API."""
        kwargs: Dict[str, Any] = {
            "modelId": self.model_id,
            "messages": messages,
        }

        if system_prompts:
            kwargs["system"] = system_prompts

        if tools:
            kwargs["toolConfig"] = {"tools": tools}
            if tool_choice:
                kwargs["toolConfig"]["toolChoice"] = tool_choice

        try:
            logger.info("bedrock_converse_start", model=self.model_id)
            response = self.client.converse(**kwargs)
            logger.info("bedrock_converse_success", usage=response.get("usage"))
            return response
        except ClientError as e:
            logger.error("bedrock_converse_failed", error=str(e))
            raise
