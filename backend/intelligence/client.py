from openai import OpenAI
from ..config import settings
from ..logger import logger

class AIClient:
    """
    Centralized LLM client to avoid redundant initializations and
    ensure consistent use of environment-based configuration.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AIClient, cls).__new__(cls)

            # Use Groq if available, otherwise OpenAI
            api_key = settings.groq_api_key or settings.openai_api_key
            base_url = "https://api.groq.com/openai/v1" if settings.groq_api_key else settings.openai_base_url

            if not api_key:
                logger.error("AIClient: No API key provided (GROQ_API_KEY or OPENAI_API_KEY)")

            cls._instance.client = OpenAI(
                api_key=api_key,
                base_url=base_url
            )
            cls._instance.model = settings.llm_model
            logger.info(f"AIClient initialized with model: {cls._instance.model}")

        return cls._instance

# Global singleton instance
ai_client = AIClient()
