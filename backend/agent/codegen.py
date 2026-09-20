"""Code generation via Amazon Bedrock.

Takes a resolved prompt (with clarify answers merged) and produces
app source code as a string. The planner calls this as one step in
its ReAct loop.
"""

from __future__ import annotations

import logging

from backend.agent.llm_client import invoke_model

logger = logging.getLogger(__name__)

CODEGEN_SYSTEM_PROMPT = """\
You are a code generator for a small-software platform. Given a user's
app description (and any clarification answers), generate a complete,
working, single-file HTML web application.

Requirements:
1. The app must be self-contained in a single HTML file.
2. Include all CSS (inside <style>) and JavaScript (inside <script>) inline.
3. Use modern, clean UI (Tailwind via CDN is permitted if helpful, or vanilla CSS).
4. The app must be fully functional in the browser with no backend required (use localStorage for data if needed).
5. Return ONLY the HTML source code — no markdown fences, no explanation.
"""


async def generate_code(
    prompt: str,
    clarifications: dict | None = None,
    *,
    model_id: str = "",
    region: str = "ap-south-1",
) -> str:
    """Generate app source code from a resolved prompt.

    Parameters
    ----------
    prompt:
        The user's original app request.
    clarifications:
        Optional dict of clarification answers merged into the context.
    model_id:
        Bedrock model identifier.
    region:
        AWS region.

    Returns
    -------
    str
        The generated Python source code.
    """
    full_prompt = prompt
    if clarifications:
        clarify_text = "\n".join(
            f"- {k}: {v}" for k, v in clarifications.items()
        )
        full_prompt = (
            f"{prompt}\n\nClarification answers:\n{clarify_text}"
        )

    logger.info("Generating code for prompt (len=%d)", len(full_prompt))

    code = invoke_model(
        full_prompt,
        system=CODEGEN_SYSTEM_PROMPT,
        model_id=model_id,
        region=region,
        max_tokens=8192,
        temperature=0.2,
    )

    # Strip markdown fences if the model wrapped the code
    code = _strip_code_fences(code)

    return code


def _strip_code_fences(text: str) -> str:
    """Remove markdown code fences from generated code."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first line (```python or ```)
        lines = lines[1:]
        # Remove last line if it's a closing fence
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)
    return text.strip()
