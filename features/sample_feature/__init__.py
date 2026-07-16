from livekit.agents import function_tool

@function_tool
async def echo_text(text: str) -> str:
    """Return the same text passed in. Useful test tool for integrations."""
    return text

@function_tool
async def feature_status() -> dict:
    """Return a small status object for the sample feature."""
    return {"name": "sample_feature", "status": "ok"}
