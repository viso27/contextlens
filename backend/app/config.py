import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URI: str = os.getenv("MONGO_URI", "")
    DB_NAME: str = os.getenv("DB_NAME", "contextlens_db")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    DEFAULT_MODEL: str = "openrouter/free"

    class Config:
        env_file = "../.env"
        extra = "ignore"

settings = Settings()