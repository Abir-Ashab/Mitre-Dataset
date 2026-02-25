"""
Application configuration management.
Loads environment variables and provides typed settings.
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    RELOAD: bool = True
    
    # Model Configuration
    BASE_MODEL: str = "Qwen/Qwen2.5-1.5B-Instruct"
    MODEL_PATH: str = r"E:\Hacking\Mitre-Dataset\fine_tuned_model"
    DEVICE: str = "cuda"  # cuda or cpu
    
    # MongoDB Configuration
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "mitre_attack_logs"
    
    # CORS Origins
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    # Model Parameters (MATCHING METRICS NOTEBOOK + TRAINING DATA EXACTLY)
    MAX_INPUT_CHARS: int = 6000      # Match metrics notebook
    MAX_LENGTH_TOKENS: int = 3072    # Match metrics notebook
    MAX_NEW_TOKENS: int = 100        # Status (3) + Techniques (15) + Reason (80)
    TEMPERATURE: float = 0.1         # Very low temp = very conservative (minimize false positives)
    TOP_P: float = 0.9               # Match metrics notebook
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
