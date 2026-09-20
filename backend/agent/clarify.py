"""Ambiguity-check pass — structured JSON output from Bedrock.

Before generating any code, this module analyses the user's prompt to
detect underspecified aspects that would materially change the resulting
app (data fields, roles/permissions, single vs. multi-user, etc.).

Returns 0–3 targeted questions, each with a suggested default and a
brief ``why_it_matters`` explanation.
"""

from __future__ import annotations

import logging

from backend.agent.llm_client import invoke_model_json
from backend.models.app import ClarifyQuestion, ClarifyResponse

logger = logging.getLogger(__name__)

CLARIFY_SYSTEM_PROMPT = """\
You are a requirements analyst for a small-software generation platform.

Given a user's plain-language app request, decide whether the request is
ambiguous in ways that would **materially change** the generated app's
structure, data model, or behaviour. Minor cosmetic decisions (colour
scheme, exact button text) do NOT count — only ask about things where
the wrong assumption would produce a fundamentally different app.

Rules:
1. If the request is clear enough to build unambiguously, return
   {"needs_clarification": false, "questions": []}.
2. If clarification is needed, return up to 3 questions. Each question
   MUST include:
   - "question": a short, specific question
   - "suggested_default": a sensible default the user can tap to accept
   - "why_it_matters": one sentence explaining why this changes the app
3. Never ask open-ended questions. Every question must have a concrete
   suggested_default.
4. Return ONLY the JSON object — no prose, no markdown.

JSON schema:
{
  "needs_clarification": boolean,
  "questions": [
    {
      "question": string,
      "suggested_default": string,
      "why_it_matters": string
    }
  ]
}
"""


async def check_ambiguity(
    prompt: str,
    *,
    model_id: str = "",
    region: str = "ap-south-1",
    credentials: dict | None = None,
) -> ClarifyResponse:
    """Analyse the user prompt for underspecified aspects.

    Parameters
    ----------
    prompt:
        The user's raw app request.
    model_id:
        Bedrock model identifier.
    region:
        AWS region.
    credentials:
        Optional user BYOK AWS credentials.

    Returns
    -------
    ClarifyResponse
        Contains ``needs_clarification`` and up to 3 ``ClarifyQuestion``s.
    """
    logger.info("Running ambiguity check on prompt (len=%d)", len(prompt))

    raw = invoke_model_json(
        prompt,
        system=CLARIFY_SYSTEM_PROMPT,
        model_id=model_id,
        region=region,
        credentials=credentials,
    )

    # Validate through Pydantic
    questions = [
        ClarifyQuestion(**q)
        for q in raw.get("questions", [])
    ]

    return ClarifyResponse(
        needs_clarification=raw.get("needs_clarification", len(questions) > 0),
        questions=questions,
    )
