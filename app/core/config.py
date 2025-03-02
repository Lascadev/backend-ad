import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "AD"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    SQLALCHEMY_DATABASE_URL: str = "postgresql://postgres:postgres@localhost/ad"

    class Config: 
        env_file = ".env"

settings = Settings()

print(settings.SECRET_KEY)