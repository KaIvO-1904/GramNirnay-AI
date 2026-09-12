from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List
from pathlib import Path
import os

# Locate project data directory dynamically
ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DATA_DIR = str(ROOT_DIR / "data") if (ROOT_DIR / "data").exists() else "data"

class Settings(BaseSettings):
    """
    Application settings managed via environment variables.
    """
    # API Keys and URLs
    openai_api_key: Optional[str] = None
    openai_base_url: Optional[str] = None
    groq_api_key: Optional[str] = None # Added for free LLM/STT
    llm_model: str = "llama-3.3-70b-versatile" # Default to Groq Llama 3
    stt_model: str = "whisper-large-v3" # Default to Groq Whisper

    # Backend Config
    app_title: str = "GramNirnay.ai Backend"
    app_debug: bool = False
    demo_mode: bool = False
    app_port: int = 8000
    app_host: str = "0.0.0.0"
    allowed_origins: List[str] = ["*"]

    # Data paths - auto resolved to d:/Projects/SIH/data
    data_dir: str = DEFAULT_DATA_DIR

    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
