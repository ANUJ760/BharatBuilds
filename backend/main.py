from fastapi import FastAPI

app = FastAPI(
    title="BharatBuilds API",
    version="0.1.0",
    description="A cloud for small software — prompt to live app in under a minute.",
)


@app.get("/health")
async def health():
    """Liveness check."""
    return {"status": "ok"}
