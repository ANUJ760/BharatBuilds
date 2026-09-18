"""Amazon Bedrock client wrapper.

Thin wrapper around ``boto3``'s ``bedrock-runtime`` ``invoke_model``,
with exponential-backoff retry logic and a helper for forcing structured
JSON output.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

# ── Retry config ─────────────────────────────────────────────────────────

MAX_RETRIES = 3
BASE_DELAY_S = 1.0  # exponential backoff: 1s, 2s, 4s


def _get_client(region: str = "ap-south-1"):
    """Return a Bedrock Runtime client."""
    return boto3.client("bedrock-runtime", region_name=region)


# ── Core invocation ──────────────────────────────────────────────────────


def invoke_model(
    prompt: str,
    *,
    system: str = "",
    model_id: str = "",
    region: str = "ap-south-1",
    max_tokens: int = 4096,
    temperature: float = 0.3,
) -> str:
    """Invoke a Bedrock model and return the response text.

    Retries up to ``MAX_RETRIES`` times on throttling or transient
    errors with exponential backoff.

    Parameters
    ----------
    prompt:
        The user message / prompt.
    system:
        Optional system prompt.
    model_id:
        Bedrock model identifier (e.g. ``deepseek.v3-1``).
    region:
        AWS region.
    max_tokens:
        Maximum tokens in the response.
    temperature:
        Sampling temperature.

    Returns
    -------
    str
        The model's text response.

    Raises
    ------
    ClientError
        If all retries are exhausted.
    """
    client = _get_client(region=region)

    messages = [{"role": "user", "content": prompt}]

    body: dict[str, Any] = {
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    if system:
        body["system"] = system

    last_error: Exception | None = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = client.invoke_model(
                modelId=model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(body),
            )
            response_body = json.loads(response["body"].read())
            return _extract_text(response_body)
        except ClientError as exc:
            error_code = exc.response.get("Error", {}).get("Code", "")
            if error_code in (
                "ThrottlingException",
                "ServiceUnavailableException",
                "ModelTimeoutException",
            ) and attempt < MAX_RETRIES:
                delay = BASE_DELAY_S * (2 ** attempt)
                logger.warning(
                    "Bedrock call failed (attempt %d/%d, code=%s), retrying in %.1fs",
                    attempt + 1,
                    MAX_RETRIES + 1,
                    error_code,
                    delay,
                )
                time.sleep(delay)
                last_error = exc
            else:
                raise
    # Should not reach here, but satisfy type checker
    raise last_error  # type: ignore[misc]


def invoke_model_json(
    prompt: str,
    *,
    system: str = "",
    model_id: str = "",
    region: str = "ap-south-1",
    max_tokens: int = 4096,
    temperature: float = 0.0,
) -> dict[str, Any]:
    """Invoke a Bedrock model and parse the response as JSON.

    Uses lower temperature (0.0 by default) and instructs the model
    to respond with valid JSON only. Falls back to extracting a JSON
    block from the response if the full text isn't valid JSON.

    Raises
    ------
    ValueError
        If the response cannot be parsed as JSON.
    """
    json_system = (
        f"{system}\n\nRespond with valid JSON only. "
        "No markdown fences, no explanation — just the JSON object."
        if system
        else "Respond with valid JSON only. No markdown fences, no explanation — just the JSON object."
    )

    raw = invoke_model(
        prompt,
        system=json_system,
        model_id=model_id,
        region=region,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return _parse_json_response(raw)


# ── Helpers ──────────────────────────────────────────────────────────────


def _extract_text(response_body: dict[str, Any]) -> str:
    """Extract the text content from a Bedrock response body.

    Handles both the Messages API format (``content[0].text``) and the
    older ``completion`` format.
    """
    # Messages API format
    if "content" in response_body and isinstance(response_body["content"], list):
        for block in response_body["content"]:
            if isinstance(block, dict) and block.get("type") == "text":
                return block["text"]
            if isinstance(block, str):
                return block
    # Older completion format
    if "completion" in response_body:
        return response_body["completion"]
    # DeepSeek format
    if "choices" in response_body:
        choices = response_body["choices"]
        if choices and "message" in choices[0]:
            return choices[0]["message"].get("content", "")
    # Fallback: stringify the whole body
    return json.dumps(response_body)


def _parse_json_response(raw: str) -> dict[str, Any]:
    """Parse a model response as JSON, tolerating markdown fences."""
    text = raw.strip()
    # Strip markdown code fences if present
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first and last lines (fences)
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        # Try to find a JSON object in the text
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                pass
        raise ValueError(f"Failed to parse model response as JSON: {raw[:200]}") from exc
