import os
from pydantic_settings import BaseSettings
from typing import List
from enum import Enum
# In config.py or ai_analyser.py
import os
import litellm
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()
class LLMProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    CREW_AI = "crew_ai"

class Settings(BaseSettings):
    #API_VERSION: str = "1.0.0"
    DEBUG: bool = True

    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: List[str] = [".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".cpp", ".c", ".h", ".hpp"]
    LLM_PROVIDER: LLMProvider = LLMProvider.CREW_AI

    # OpenAI Configuration
    OPENAI_API_KEY:str = os.getenv("OPENAI_API_KEY", "").strip()
    TEXT_COMPLETION_OPENAI_API_KEY:str  = os.getenv("TEXT_COMPLETION_OPENAI_API_KEY", "").strip()
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo-instruct")

    # # Anthropic Configuration
    # ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    # ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229")

    # # Google AI Configuration
    # GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    # GOOGLE_MODEL: str = os.getenv("GOOGLE_MODEL", "gemini-pro")

    # # Crew AI Configuration
    CREW_AI_TEMPERATURE: float = 0.7
    CREW_AI_MAX_TOKENS: int = 4096

    # Redis Configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    REDIS_TTL: int = 3600  # 1 hour

    # CORS Configuration
    CORS_ORIGINS: List[str] = ["*"]

    # Rate Limiting
    RATE_LIMIT_CALLS: int = 50  # Adjust based on provider limits
    RATE_LIMIT_PERIOD: int = 60

    # Concurrency
    MAX_CONCURRENT_ANALYSES: int = 5

    class Config:
        env_file = ".env"
        extra = "ignore"
        env_file_encoding = "utf-8"

settings = Settings()