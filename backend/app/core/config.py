from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Buqacha.uz MVP"
    DATABASE_URL: str = "sqlite+aiosqlite:///./chorva.db"
    
    # Bot va API sozlamalari (.env orqali boshqariladi)
    BOT_TOKEN: str
    CHANNEL_ID: str = "@chorvabozor_test"
    FRONTEND_URL: str = "http://localhost:5173"
    API_URL: str = "http://localhost:8000/api"
    SUPPORT_GROUP_ID: str = "0"

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
