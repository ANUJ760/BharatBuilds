"""Google Gemini API client wrapper.

Thin wrapper around ``google-generativeai``, replacing Bedrock.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from google.api_core.exceptions import GoogleAPICallError, RetryError, InternalServerError, TooManyRequests, ResourceExhausted

from backend.config import get_settings

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
BASE_DELAY_S = 1.0


def _get_model(
    model_id: str,
    system: str = "",
    temperature: float = 0.3,
    max_tokens: int = 4096,
    response_mime_type: str = "text/plain"
) -> genai.GenerativeModel:
    settings = get_settings()
    genai.configure(api_key=settings.gemini_api_key)
    
    effective_model = model_id if (model_id and "gemini" in model_id.lower()) else (getattr(settings, "gemini_model_id", None) or "gemini-2.5-flash")
    
    generation_config = genai.types.GenerationConfig(
        temperature=temperature,
        max_output_tokens=max_tokens,
        response_mime_type=response_mime_type,
    )
    
    return genai.GenerativeModel(
        model_name=effective_model,
        system_instruction=system if system else None,
        generation_config=generation_config,
    )


def invoke_model(
    prompt: str,
    *,
    system: str = "",
    model_id: str = "",
    region: str = "", # ignored for Gemini
    max_tokens: int = 8192,
    temperature: float = 0.3,
) -> str:
    """Invoke a Gemini model and return the response text."""
    model = _get_model(
        model_id=model_id, 
        system=system, 
        temperature=temperature, 
        max_tokens=max_tokens
    )

    last_error: Exception | None = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = model.generate_content(
                prompt,
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                }
            )
            return response.text
        except (GoogleAPICallError, RetryError, Exception) as exc:
            if attempt < MAX_RETRIES:
                delay = BASE_DELAY_S * (2 ** attempt)
                logger.warning(
                    "Gemini call failed (attempt %d/%d), retrying in %.1fs",
                    attempt + 1,
                    MAX_RETRIES + 1,
                    delay,
                )
                time.sleep(delay)
                last_error = exc
            else:
                raise
    raise last_error # type: ignore


def invoke_model_json(
    prompt: str,
    *,
    system: str = "",
    model_id: str = "",
    region: str = "", # ignored for Gemini
    max_tokens: int = 8192,
    temperature: float = 0.0,
) -> dict[str, Any]:
    """Invoke a Gemini model and parse the response as JSON."""
    json_system = (
        f"{system}\n\nRespond with valid JSON only. "
        "No markdown fences, no explanation — just the JSON object."
        if system
        else "Respond with valid JSON only. No markdown fences, no explanation — just the JSON object."
    )

    model = _get_model(
        model_id=model_id,
        system=json_system,
        temperature=temperature,
        max_tokens=max_tokens,
        response_mime_type="application/json"
    )

    last_error: Exception | None = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = model.generate_content(
                prompt,
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                }
            )
            return _parse_json_response(response.text)
        except (GoogleAPICallError, RetryError, Exception) as exc:
            if attempt < MAX_RETRIES:
                delay = BASE_DELAY_S * (2 ** attempt)
                logger.warning(
                    "Gemini JSON call failed (attempt %d/%d), retrying in %.1fs. Error: %s",
                    attempt + 1,
                    MAX_RETRIES + 1,
                    delay,
                    exc,
                )
                time.sleep(delay)
                last_error = exc
            else:
                raise
    raise last_error # type: ignore


def _parse_json_response(raw: str) -> dict[str, Any]:
    """Parse a model response as JSON, tolerating markdown fences."""
    text = raw.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                pass
        raise ValueError(f"Failed to parse model response as JSON: {raw[:200]}") from exc
