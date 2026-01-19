"""Configuration management for the research agent"""

import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()


class Config:
    """Configuration class for managing API keys and settings"""
    
    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
    
    # Model Configuration
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gemini-3-flash-preview")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "4000"))
    
    # Research Configuration
    MAX_SEARCH_RESULTS: int = 10
    MAX_CONTENT_LENGTH: int = 50000  # Max characters per source
    RESEARCH_DEPTH: str = os.getenv("RESEARCH_DEPTH", "medium")  # shallow, medium, deep
    
    # Output Configuration
    OUTPUT_DIR: str = "outputs"
    REPORT_FORMAT: str = "markdown"  # markdown, html, pdf
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required API keys are set"""
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required. Please set it in your .env file")
        if not cls.TAVILY_API_KEY:
            print("Warning: TAVILY_API_KEY not set. Web search may be limited.")
        return True
    
    @classmethod
    def get_output_path(cls, filename: str) -> str:
        """Get full path for output file"""
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)
        return os.path.join(cls.OUTPUT_DIR, filename)
