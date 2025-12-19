from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    # App Settings
    PROJECT_NAME: str = "NxtDo"
    
    # Firebase / GCP Settings (Injected via .env locally or GCP Console in Prod)
    GCP_PROJECT_ID: str 
    DATABASE_URL: str
    
    # Authentication (Microsoft)
    AZURE_CLIENT_ID: str
    AZURE_TENANT_ID: str

    # Tell Pydantic to look for a .env file locally
    model_config = SettingsConfigDict(env_file=".env")

@lru_cache
def get_settings():
    return Settings()

settings = get_settings()