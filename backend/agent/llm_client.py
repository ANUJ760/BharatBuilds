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
    credentials = kwargs.pop("credentials", None)
    
    # Use Bedrock if user provided BYOK credentials OR if we have a default bedrock model configured
    if credentials or getattr(settings, "bedrock_model_id", None):
        try:
            if credentials:
                kwargs["credentials"] = credentials
            return bedrock_client.invoke_model(*args, **kwargs)
        except Exception as e:
            if credentials:
                logger.warning(f"User BYOK Bedrock invocation failed: {e}. Falling back to default Gemini API.")
            else:
                logger.warning(f"Bedrock invocation failed: {e}. Falling back to Gemini API.")
            
    # Fallback to Gemini
    kwargs.pop("region", None)
    kwargs.pop("credentials", None)
    gemini_model = getattr(settings, "gemini_model_id", "gemini-2.5-flash")
    current_model = kwargs.get("model_id", "")
    if not current_model or "gemini" not in current_model.lower():
        kwargs["model_id"] = gemini_model
    return gemini_client.invoke_model(*args, **kwargs)


def invoke_model_json(*args, **kwargs) -> dict[str, Any]:
    settings = get_settings()
    credentials = kwargs.pop("credentials", None)
    
    if credentials or getattr(settings, "bedrock_model_id", None):
        try:
            if credentials:
                kwargs["credentials"] = credentials
            return bedrock_client.invoke_model_json(*args, **kwargs)
        except Exception as e:
            if credentials:
                logger.warning(f"User BYOK Bedrock JSON invocation failed: {e}. Falling back to Gemini API.")
            else:
                logger.warning(f"Bedrock JSON invocation failed: {e}. Falling back to Gemini API.")
            
    # Fallback to Gemini
    kwargs.pop("region", None)
    kwargs.pop("credentials", None)
    gemini_model = getattr(settings, "gemini_model_id", "gemini-2.5-flash")
    current_model = kwargs.get("model_id", "")
    if not current_model or "gemini" not in current_model.lower():
        kwargs["model_id"] = gemini_model
    return gemini_client.invoke_model_json(*args, **kwargs)
