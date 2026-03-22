"""Configuration management for the research agent"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration class for managing API keys and settings"""

    # -----------------------------------------------------------------------
    # API Keys
    # -----------------------------------------------------------------------
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")

    # -----------------------------------------------------------------------
    # LangSmith Observability (optional)
    # -----------------------------------------------------------------------
    LANGSMITH_API_KEY: str = os.getenv("LANGSMITH_API_KEY", "")
    LANGSMITH_PROJECT: str = os.getenv("LANGSMITH_PROJECT", "research-agent")

    # -----------------------------------------------------------------------
    # Model Configuration
    # -----------------------------------------------------------------------
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gemini-2.0-flash")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "4000"))

    # -----------------------------------------------------------------------
    # Research Configuration
    # -----------------------------------------------------------------------
    MAX_SEARCH_RESULTS: int = int(os.getenv("MAX_SEARCH_RESULTS", "10"))
    MAX_CONTENT_LENGTH: int = int(os.getenv("MAX_CONTENT_LENGTH", "50000"))
    RESEARCH_DEPTH: str = os.getenv("RESEARCH_DEPTH", "medium")
    MAX_CONCURRENT_SEARCHES: int = int(os.getenv("MAX_CONCURRENT_SEARCHES", "5"))

    # -----------------------------------------------------------------------
    # Output Configuration
    # -----------------------------------------------------------------------
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "outputs")
    REPORT_FORMAT: str = os.getenv("REPORT_FORMAT", "markdown")

    # -----------------------------------------------------------------------
    # Persistence
    # -----------------------------------------------------------------------
    SQLITE_DB_PATH: str = os.getenv("SQLITE_DB_PATH", "data/research.db")
    CHROMA_PERSIST_PATH: str = os.getenv("CHROMA_PERSIST_PATH", "data/chroma")

    # -----------------------------------------------------------------------
    # API Server
    # -----------------------------------------------------------------------
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))

    # -----------------------------------------------------------------------
    # Methods
    # -----------------------------------------------------------------------
    @classmethod
    def validate(cls) -> bool:
        """Validate that required API keys are set."""
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required. Please set it in your .env file")
        if not cls.TAVILY_API_KEY:
            print("Warning: TAVILY_API_KEY not set. Web search will fall back to DuckDuckGo.")
        return True

    @classmethod
    def get_output_path(cls, filename: str) -> str:
        """Get full path for output file, creating the directory if needed."""
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)
        return os.path.join(cls.OUTPUT_DIR, filename)

    @classmethod
    def get_data_dir(cls) -> str:
        """Ensure the data/ directory exists and return its path."""
        os.makedirs("data", exist_ok=True)
        return "data"
