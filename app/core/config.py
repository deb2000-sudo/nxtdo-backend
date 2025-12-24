from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    # App Settings
    PROJECT_NAME: str = "NxtDo"
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # Firebase / GCP Settings
    GCP_PROJECT_ID: str = "nxtdo-dev"
    
    # Firebase Service Account Key (JSON string)
    FIREBASE_SERVICE_ACCOUNT_KEY: Optional[str] = None
    
    # Database URL (optional, for backward compatibility)
    DATABASE_URL: Optional[str] = None
    
    # Authentication (Microsoft) - made optional for now
    AZURE_CLIENT_ID: Optional[str] = None
    AZURE_TENANT_ID: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env.local",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    def get_firebase_config(self) -> dict:
        """Get Firebase configuration based on environment"""
        if self.ENVIRONMENT == "production":
            return {
                "project_id": "nxtdo-prod",
                "storage_bucket": "nxtdo-prod.firebasestorage.app",
                "database_id": "nxtdo-prod-db"
            }
        else:
            return {
                "project_id": "nxtdo-dev",
                "storage_bucket": "nxtdo-dev.firebasestorage.app",
                "database_id": "nxtdo-dev-db"
            }

@lru_cache
def get_settings():
    return Settings()

settings = get_settings()