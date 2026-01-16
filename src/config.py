"""
Configuration module for API clients.
Loads settings from environment variables.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
load_dotenv()


class Config:
    """Configuration settings for API clients."""

    # Gemini / Nano Banana Pro
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta"

    # Nano Banana Models
    NANO_BANANA_MODEL: str = "gemini-2.0-flash-exp"  # Fast model
    NANO_BANANA_PRO_MODEL: str = "gemini-2.0-flash-exp"  # Pro model (use same for now)

    # Kling AI via PiAPI
    PIAPI_API_KEY: str = os.getenv("PIAPI_API_KEY", "")
    PIAPI_BASE_URL: str = "https://api.piapi.ai/api/v1"

    # Direct Kling API (alternative)
    KLING_API_KEY: str = os.getenv("KLING_API_KEY", "")
    KLING_BASE_URL: str = "https://api.klingai.com/v1"

    # Output settings
    OUTPUT_DIR: Path = Path(os.getenv("OUTPUT_DIR", "./output"))

    @classmethod
    def validate(cls) -> dict[str, bool]:
        """Check which APIs are configured."""
        return {
            "nano_banana": bool(cls.GEMINI_API_KEY),
            "kling_piapi": bool(cls.PIAPI_API_KEY),
            "kling_direct": bool(cls.KLING_API_KEY),
        }

    @classmethod
    def ensure_output_dir(cls) -> Path:
        """Create output directory if it doesn't exist."""
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        return cls.OUTPUT_DIR
