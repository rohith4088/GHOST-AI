# import os
# from pydantic_settings import BaseSettings
# from typing import List
# from enum import Enum
# # In config.py or ai_analyser.py
# import os
# import litellm
# from openai import OpenAI
# from dotenv import load_dotenv


# load_dotenv()
# class LLMProvider(Enum):
#     OPENAI = "openai"
#     ANTHROPIC = "anthropic"
#     GOOGLE = "google"
#     CREW_AI = "crew_ai"

# class Settings(BaseSettings):
#     #API_VERSION: str = "1.0.0"
#     DEBUG: bool = True

#     MAX_FILE_SIZE_MB: int = 50
#     ALLOWED_EXTENSIONS: List[str] = [".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".cpp", ".c", ".h", ".hpp"]
#     LLM_PROVIDER: LLMProvider = LLMProvider.CREW_AI

#     # OpenAI Configuration
#     OPENAI_API_KEY:str = os.getenv("OPENAI_API_KEY", "").strip()
#     TEXT_COMPLETION_OPENAI_API_KEY:str  = os.getenv("TEXT_COMPLETION_OPENAI_API_KEY", "").strip()
#     OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo-instruct")

#     # # Anthropic Configuration
#     # ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
#     # ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229")

#     # # Google AI Configuration
#     GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
#     GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

#     # # Crew AI Configuration
#     CREW_AI_TEMPERATURE: float = 0.7
#     CREW_AI_MAX_TOKENS: int = 4096

#     # Redis Configuration
#     REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
#     REDIS_TTL: int = 3600  # 1 hour

#     # CORS Configuration
#     CORS_ORIGINS: List[str] = ["*"]

#     # Rate Limiting
#     RATE_LIMIT_CALLS: int = 2  
#     RATE_LIMIT_PERIOD: int = 1000

#     # Concurrency
#     MAX_CONCURRENT_ANALYSES: int = 5

#     class Config:
#         env_file = ".env"
#         extra = "ignore"
#         env_file_encoding = "utf-8"

# settings = Settings()



import os
from pydantic_settings import BaseSettings
from typing import List, Optional
from enum import Enum
from dotenv import load_dotenv

load_dotenv()

class LLMProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    CREW_AI = "crew_ai"
    LOCAL_LLM = "local_llm" 

class Settings(BaseSettings):
    # Existing configurations
    DEBUG: bool = True
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: List[str] = [".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".cpp", ".c", ".h", ".hpp"]
    
    # LLM Provider Configuration
    LLM_PROVIDER: LLMProvider = LLMProvider.LOCAL_LLM
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "").strip()
    TEXT_COMPLETION_OPENAI_API_KEY: str = os.getenv("TEXT_COMPLETION_OPENAI_API_KEY", "").strip()
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo-instruct")
    
    # Local LLM Configuration
    LOCAL_LLM_BASE_URL: str = os.getenv("LOCAL_LLM_BASE_URL", "http://192.168.0.113:1234")
    LOCAL_LLM_MODEL: str = os.getenv("LOCAL_LLM_MODEL", "llama-3.2-3b-instruct")
    
    # Gemini Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    
    # Crew AI Configuration
    CREW_AI_TEMPERATURE: float = 0.7
    CREW_AI_MAX_TOKENS: int = 4096
    
    # Redis Configuration
    REDIS_URL: str = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    REDIS_TIMEOUT: int = 10 
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = ["*"]
    
    # Rate Limiting
    RATE_LIMIT_CALLS: int = 2
    RATE_LIMIT_PERIOD: int = 1000
    
    # Concurrency
    MAX_CONCURRENT_ANALYSES: int = 5

    class Config:
        env_file = ".env"
        extra = "ignore"
        env_file_encoding = "utf-8"

# Create settings instance
settings = Settings()