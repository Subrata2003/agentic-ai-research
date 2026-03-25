"""
LangSmith observability setup.

Call setup_tracing() once at application startup (FastAPI startup event,
top of main.py, etc.). When LANGSMITH_API_KEY is present, every LangChain
LLM call across all agents is automatically traced — latency, tokens,
chain structure — with zero additional code changes.
"""

import os


def setup_tracing() -> None:
    """Configure LangSmith tracing if an API key is available."""
    # Import here to avoid circular imports at module level
    from src.utils.config import Config

    if Config.LANGSMITH_API_KEY:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
        os.environ["LANGCHAIN_API_KEY"] = Config.LANGSMITH_API_KEY
        os.environ["LANGCHAIN_PROJECT"] = Config.LANGSMITH_PROJECT
        print(f"[Tracing] LangSmith enabled — project: {Config.LANGSMITH_PROJECT}")
    else:
        os.environ["LANGCHAIN_TRACING_V2"] = "false"
