"""Ambiguity-check pass — structured JSON output from Bedrock."""


async def check_ambiguity(prompt: str) -> dict:
    """
    Analyse the user prompt for underspecified aspects that would
    materially change the generated app. Returns up to 3 questions
    with suggested defaults.
    """
    # TODO: call Bedrock with a clarify-specific system prompt
    pass
