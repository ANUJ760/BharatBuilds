"""Unified LLM client with Bedrock-first logic and Gemini fallback."""

from __future__ import annotations

import logging
from typing import Any

from backend.config import get_settings
from backend.agent import bedrock_client
from backend.agent import gemini_client

logger = logging.getLogger(__name__)

def invoke_model(*args, **kwargs) -> str:
    settings = get_settings()
    
    if getattr(settings, "bedrock_model_id", None):
        try:
            return bedrock_client.invoke_model(*args, **kwargs)
        except Exception as e:
            logger.warning(f"Bedrock invocation failed: {e}. Falling back to Gemini API.")
            
    # Fallback to Gemini
    kwargs.pop("region", None)
    if "model_id" not in kwargs or not kwargs["model_id"]:
        kwargs["model_id"] = getattr(settings, "gemini_model_id", "gemini-2.5-flash")
    return gemini_client.invoke_model(*args, **kwargs)


def invoke_model_json(*args, **kwargs) -> dict[str, Any]:
    settings = get_settings()
    
    if getattr(settings, "bedrock_model_id", None):
        try:
            return bedrock_client.invoke_model_json(*args, **kwargs)
        except Exception as e:
            logger.warning(f"Bedrock JSON invocation failed: {e}. Falling back to Gemini API.")
            
    # Fallback to Gemini
    kwargs.pop("region", None)
    if "model_id" not in kwargs or not kwargs["model_id"]:
        kwargs["model_id"] = getattr(settings, "gemini_model_id", "gemini-2.5-flash")
    return gemini_client.invoke_model_json(*args, **kwargs)
