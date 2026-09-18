"""Fast-path deploy for lightweight apps via Lambda + Function URLs."""


async def deploy_to_lambda(app_id: str, code: str) -> str:
    """
    Deploy lightweight app as a Lambda function with a Function URL.
    Returns the live URL.
    """
    # TODO: package code, create/update Lambda, enable Function URL
    pass
