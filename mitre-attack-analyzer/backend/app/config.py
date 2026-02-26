"""
Application configuration management.
Loads environment variables and provides typed settings.
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    

    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    RELOAD: bool = True
    

    BASE_MODEL: str = "Qwen/Qwen2.5-1.5B-Instruct"
    MODEL_PATH: str = r"E:\Hacking\Mitre-Dataset\fine_tuned_model"
    DEVICE: str = "cuda"
    

    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "mitre_attack_logs"
    

    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    

    MAX_INPUT_CHARS: int = 6000
    MAX_LENGTH_TOKENS: int = 3072
    MAX_NEW_TOKENS: int = 128
    TEMPERATURE: float = 0.7
    TOP_P: float = 0.9
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True



settings = Settings()
