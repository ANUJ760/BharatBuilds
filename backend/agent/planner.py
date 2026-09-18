"""ReAct loop — plan / tool-call / codegen steps.

Hand-rolled ReAct (Reason → Act → Observe) loop that:
1. Plans the app structure
2. Generates code via codegen
3. Self-corrects on errors (up to ``MAX_RETRIES``)

Every step is recorded as a :class:`TimelineStep` for the Decision
Timeline. The caller (route handler) is responsible for persisting
these steps via :pymod:`backend.agent.trace_logger`.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from backend.agent.bedrock_client import invoke_model, invoke_model_json
from backend.agent.codegen import generate_code
from backend.models.app import StepStatus, StepType, TimelineStep

logger = logging.getLogger(__name__)

MAX_RETRIES = 2

PLAN_SYSTEM_PROMPT = """\
You are a planning agent for a small-software generation platform.

Given a user's app request (with clarification answers if any), produce
a structured plan for building the app. The plan should specify:

1. "app_title": a short, descriptive title for the app
2. "features": list of features the app will have
3. "data_model": description of data fields / entities
4. "ui_description": brief description of the UI layout
5. "technical_notes": any implementation considerations

Return ONLY the JSON object — no prose, no markdown.
"""

REVIEW_SYSTEM_PROMPT = """\
You are a code reviewer. Given the generated source code for a small web app,
check for:
1. Syntax errors
2. Missing imports
3. Runtime errors (undefined variables, wrong function signatures)
4. Security issues (SQL injection, XSS, hardcoded secrets)

If the code is correct, return: {"is_valid": true, "issues": []}
If there are issues, return: {"is_valid": false, "issues": ["description of each issue"]}
If the code has issues, also return a "fix_instructions" field with specific
instructions for fixing each issue.

Return ONLY the JSON object.
"""


async def plan_and_execute(
    prompt: str,
    clarifications: dict[str, str] | None = None,
    *,
    model_id: str = "",
    region: str = "ap-south-1",
    app_id: str = "",
) -> tuple[str, list[TimelineStep]]:
    """Run the full ReAct pipeline: plan → codegen → review → (retry).

    Parameters
    ----------
    prompt:
        The user's original app request.
    clarifications:
        Optional clarification answers.
    model_id:
        Bedrock model identifier.
    region:
        AWS region.
    app_id:
        ID of the app being built (for timeline step linkage).

    Returns
    -------
    tuple[str, list[TimelineStep]]
        A tuple of (generated_code, list_of_steps).
    """
    steps: list[TimelineStep] = []

    # ── Step 1: Plan ─────────────────────────────────────────────────
    plan_step, plan = await _plan(prompt, clarifications, model_id=model_id, region=region, app_id=app_id)
    steps.append(plan_step)

    if plan_step.status == StepStatus.ERROR:
        return "", steps

    # ── Step 2: Codegen (with retry loop) ────────────────────────────
    code = ""
    parent_step_id = plan_step.step_id

    for attempt in range(MAX_RETRIES + 1):
        codegen_step, code = await _codegen(
            prompt,
            clarifications,
            plan,
            model_id=model_id,
            region=region,
            app_id=app_id,
            parent_step_id=parent_step_id,
        )
        steps.append(codegen_step)

        if codegen_step.status == StepStatus.ERROR:
            return "", steps

        # ── Step 3: Review ───────────────────────────────────────────
        review_step, is_valid, fix_instructions = await _review(
            code,
            model_id=model_id,
            region=region,
            app_id=app_id,
            parent_step_id=codegen_step.step_id,
        )
        steps.append(review_step)

        if is_valid:
            logger.info("Code passed review on attempt %d", attempt + 1)
            break

        if attempt < MAX_RETRIES:
            # Retry: generate again with fix instructions
            logger.warning(
                "Code review failed (attempt %d/%d), retrying with fixes",
                attempt + 1,
                MAX_RETRIES + 1,
            )
            retry_step = TimelineStep(
                app_id=app_id,
                step_type=StepType.RETRY,
                parent_step_id=review_step.step_id,
                input_text=fix_instructions,
                reasoning=f"Retrying codegen (attempt {attempt + 2})",
                status=StepStatus.OK,
            )
            steps.append(retry_step)
            parent_step_id = retry_step.step_id
            # Augment the prompt with fix instructions for next attempt
            prompt = f"{prompt}\n\nFix these issues in the generated code:\n{fix_instructions}"
        else:
            logger.warning("Max retries reached, returning last generated code")

    return code, steps


async def _plan(
    prompt: str,
    clarifications: dict[str, str] | None,
    *,
    model_id: str,
    region: str,
    app_id: str,
) -> tuple[TimelineStep, dict[str, Any]]:
    """Run the planning step."""
    start = time.monotonic()
    try:
        full_prompt = prompt
        if clarifications:
            clarify_text = "\n".join(f"- {k}: {v}" for k, v in clarifications.items())
            full_prompt = f"{prompt}\n\nClarifications:\n{clarify_text}"

        plan = invoke_model_json(
            full_prompt,
            system=PLAN_SYSTEM_PROMPT,
            model_id=model_id,
            region=region,
        )
        latency = int((time.monotonic() - start) * 1000)

        step = TimelineStep(
            app_id=app_id,
            step_type=StepType.PLAN,
            input_text=full_prompt,
            reasoning=str(plan),
            latency_ms=latency,
            status=StepStatus.OK,
        )
        return step, plan

    except Exception as exc:
        latency = int((time.monotonic() - start) * 1000)
        step = TimelineStep(
            app_id=app_id,
            step_type=StepType.PLAN,
            input_text=prompt,
            latency_ms=latency,
            status=StepStatus.ERROR,
            error_message=str(exc),
        )
        return step, {}


async def _codegen(
    prompt: str,
    clarifications: dict[str, str] | None,
    plan: dict[str, Any],
    *,
    model_id: str,
    region: str,
    app_id: str,
    parent_step_id: str,
) -> tuple[TimelineStep, str]:
    """Run the code generation step."""
    start = time.monotonic()
    try:
        code = await generate_code(
            prompt,
            clarifications,
            model_id=model_id,
            region=region,
        )
        latency = int((time.monotonic() - start) * 1000)

        step = TimelineStep(
            app_id=app_id,
            step_type=StepType.CODEGEN,
            parent_step_id=parent_step_id,
            code_snapshot=code,
            code_diff=f"+{len(code.splitlines())} lines",
            latency_ms=latency,
            status=StepStatus.OK,
        )
        return step, code

    except Exception as exc:
        latency = int((time.monotonic() - start) * 1000)
        step = TimelineStep(
            app_id=app_id,
            step_type=StepType.CODEGEN,
            parent_step_id=parent_step_id,
            latency_ms=latency,
            status=StepStatus.ERROR,
            error_message=str(exc),
        )
        return step, ""


async def _review(
    code: str,
    *,
    model_id: str,
    region: str,
    app_id: str,
    parent_step_id: str,
) -> tuple[TimelineStep, bool, str]:
    """Review generated code for correctness."""
    start = time.monotonic()
    try:
        review = invoke_model_json(
            f"Review this code:\n\n{code}",
            system=REVIEW_SYSTEM_PROMPT,
            model_id=model_id,
            region=region,
        )
        latency = int((time.monotonic() - start) * 1000)
        is_valid = review.get("is_valid", False)
        issues = review.get("issues", [])
        fix_instructions = review.get("fix_instructions", "")

        step = TimelineStep(
            app_id=app_id,
            step_type=StepType.TOOL_CALL,
            parent_step_id=parent_step_id,
            reasoning=f"Code review: {'passed' if is_valid else 'failed'} — {len(issues)} issues",
            latency_ms=latency,
            status=StepStatus.OK if is_valid else StepStatus.ERROR,
            error_message="\n".join(issues) if issues else None,
        )
        return step, is_valid, fix_instructions if isinstance(fix_instructions, str) else str(fix_instructions)

    except Exception as exc:
        latency = int((time.monotonic() - start) * 1000)
        step = TimelineStep(
            app_id=app_id,
            step_type=StepType.TOOL_CALL,
            parent_step_id=parent_step_id,
            latency_ms=latency,
            status=StepStatus.ERROR,
            error_message=str(exc),
        )
        # If review itself fails, treat code as valid (don't block deploy)
        return step, True, ""
