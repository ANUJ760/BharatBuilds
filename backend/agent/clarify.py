"""Clarification Engine."""
import json
from typing import Dict, Any

import structlog

from backend.agent.bedrock_client import BedrockClient

logger = structlog.get_logger(__name__)

CLARIFY_SYSTEM_PROMPT = """You are the Clarification Engine for MicroAgent.
Your job is to read a user's natural language request for a small workflow/application
and determine if critical constraints are fundamentally ambiguous.

DO NOT ASK CONVERSATIONAL QUESTIONS.
ONLY ASK ABOUT MATERIAL AMBIGUITIES, like:
- Important data fields not specified
- Specific roles/permissions not mentioned
- Unclear workflow behavior

Return ONLY valid JSON matching this schema:
{
  "needs_clarification": true/false,
  "questions": [
    {
      "question": "string",
      "suggested_default": "string"
    }
  ]
}

Maximum 3 questions. If the request is clear enough to make reasonable assumptions,
set needs_clarification to false and leave questions empty.
"""


class ClarificationEngine:
    """Determines if a workflow request needs clarification."""

    def __init__(self, bedrock_client: BedrockClient):
        self.bedrock = bedrock_client

    def evaluate_request(self, user_request: str) -> Dict[str, Any]:
        """Evaluate if the request needs clarification."""
        messages = [
            {"role": "user", "content": [{"text": user_request}]}
        ]

        system = [{"text": CLARIFY_SYSTEM_PROMPT}]

        try:
            response = self.bedrock.converse(
                messages=messages,
                system_prompts=system,
                # We could force tool use to guarantee JSON, but for this foundation
                # we'll assume the model follows the JSON instruction.
            )

            content = response["output"]["message"]["content"][0]["text"]

            # Simple parse. In prod, handle markdown stripping if model adds ```json
            result = json.loads(content)

            logger.info(
                "clarification_evaluation",
                needs_clarification=result.get("needs_clarification")
            )

            return result

        except Exception as e:
            logger.error("clarification_failed", error=str(e))
            # Safe fallback: don't block workflow creation if clarification engine fails
            return {"needs_clarification": False, "questions": []}
