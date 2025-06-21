from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    #App settings
    app_name: str = "RingkasAI"
    app_version: str = "1.0.0"
    debug: bool = True

    # CORS settings
    allowed_origins: List[str] = [
        "http://localhost:5173", 
        "http://127.0.0.1:5173"
    ]

    # Azure OpenAI setting
    azure_openai_api_key: str
    azure_openai_api_version: str
    azure_openai_endpoint: str
    azure_openai_deployment_name: str
    
    # Storage
    storage_path: str = "./app/storage"
    max_file_size_mb: int = 100
    cleanup_after_hours: int = 24

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
settings = Settings()