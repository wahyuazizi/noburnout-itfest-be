
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings."""
    
    # App settings
    app_name: str = "YouTube Transcript API"
    version: str = "1.0.0"
    debug: bool = True
    
    # Server settings
    host: str = "127.0.0.1"
    port: int = 8000
    
    # Storage settings
    base_dir: Path = Path(__file__).parent.parent
    storage_dir: Path = base_dir / "app" / "storage"
    transcripts_dir: Path = storage_dir / "transcripts"
    
    # API settings
    api_v1_prefix: str = "/api/v1"
    
    # CORS settings
    cors_origins: list = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Azure OpenAI setting
    azure_openai_api_key: str
    azure_openai_api_version: str
    azure_openai_endpoint: str
    azure_openai_deployment_name: str
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Create settings instance
settings = Settings()

# Ensure storage directories exist
def ensure_storage_dirs():
    """Create storage directories if they don't exist."""
    for dir_path in [
        settings.storage_dir,
        settings.transcripts_dir,
    ]:
        dir_path.mkdir(parents=True, exist_ok=True)

# Call on import
ensure_storage_dirs()