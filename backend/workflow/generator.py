"""Workflow generator: natural language -> structured WorkflowDefinition."""
from typing import Any, Dict, Optional

import structlog

from backend.agent.bedrock_client import BedrockClient
from backend.agent.clarify import ClarificationEngine
from backend.models.workflow import WorkflowDefinition
from backend.utils.errors import WorkflowValidationError
from backend.workflow.validator import WorkflowValidator

logger = structlog.get_logger(__name__)


WORKFLOW_GENERATION_SYSTEM_PROMPT = """You are the Workflow Generator for MicroAgent.
Your job is to convert a user's natural language request into a VALID, EXECUTABLE workflow definition.

Return ONLY valid JSON matching this schema:
{
  "name": "string",
  "description": "string",
  "trigger": { "type": "manual" | "scheduled" | "event", "schedule": "cron (optional)", "event_type": "string (optional)" },
  "inputs": ["string"],
  "steps": [
    { "tool": "string", "input": { ... }, "condition": "string (optional)" }
  ],
  "actions": [
    { "name": "string", "requires_approval": boolean, "tool": "string (optional)" }
  ],
  "allowed_tools": ["tool_name"],
  "allowed_resources": ["resource_id"]
}

CRITICAL RULES:
- Every tool referenced in steps MUST be listed in allowed_tools.
- Only use tools that are registered in the system.
- Keep workflows small and focused (max 10 steps).
- Use sensible defaults where the user was vague.
- Do NOT include conversational text, only the JSON object.
"""


class WorkflowGenerator:
    """Generates a validated WorkflowDefinition from a natural language prompt."""

    def __init__(
        self,
        bedrock_client: BedrockClient,
        clarification_engine: ClarificationEngine,
        validator: WorkflowValidator,
    ):
        self.bedrock = bedrock_client
        self.clarify = clarification_engine
        self.validator = validator

    async def generate(
        self,
        user_request: str,
        available_tools: list[str],
        organization_id: str,
    ) -> WorkflowDefinition:
        """Generate a workflow definition from a natural language request."""
        logger.info("workflow_generation_started", request_preview=user_request[:80])

        # 1. Clarify ambiguities
        clarification = self.clarify.evaluate_request(user_request)
        if clarification.get("needs_clarification"):
            logger.warning("workflow_needs_clarification", questions=clarification.get("questions"))
            raise WorkflowValidationError(
                "Workflow generation requires clarification",
                details={"questions": clarification.get("questions")},
            )

        # 2. Build prompt with available tools
        tools_list = ", ".join(available_tools) if available_tools else "none"
        prompt = (
            f"User request:\n{user_request}\n\n"
            f"Available tools: {tools_list}\n\n"
            f"Generate the workflow JSON now."
        )

        # 3. Call Bedrock
        messages = [{"role": "user", "content": [{"text": prompt}]}]
        system = [{"text": WORKFLOW_GENERATION_SYSTEM_PROMPT}]

        try:
            response = self.bedrock.converse(messages=messages, system_prompts=system)
            content = response["output"]["message"]["content"][0]["text"]
        except Exception as e:
            logger.error("bedrock_generation_failed", error=str(e))
            raise WorkflowValidationError(
                f"Failed to generate workflow: {str(e)}",
            )

        # 4. Parse JSON (strip markdown fences if present)
        raw_json = self._extract_json(content)

        try:
            import json
            definition_dict = json.loads(raw_json)
        except json.JSONDecodeError as e:
            logger.error("workflow_json_parse_failed", raw=raw_json[:200])
            raise WorkflowValidationError(
                f"Generated workflow was not valid JSON: {str(e)}",
                details={"raw_content": raw_json[:500]},
            )

        # 5. Build typed model
        try:
            workflow_def = WorkflowDefinition(**definition_dict)
        except Exception as e:
            logger.error("workflow_model_build_failed", error=str(e))
            raise WorkflowValidationError(
                f"Failed to build WorkflowDefinition model: {str(e)}",
                details={"definition": definition_dict},
            )

        # 6. Validate
        self.validator.validate(workflow_def)

        logger.info("workflow_generation_success", name=workflow_def.name)
        return workflow_def

    @staticmethod
    def _extract_json(content: str) -> str:
        """Extract JSON from a markdown code block if present."""
        content = content.strip()
        if content.startswith("```"):
            # Strip opening fence and optional language
            lines = content.split("\n")
            # Remove first line (```json or ```)
            if lines[0].startswith("```"):
                lines = lines[1:]
            # Remove trailing fence
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            content = "\n".join(lines)
        return content.strip()