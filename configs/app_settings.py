from pydantic_settings import BaseSettings
from typing import List
from datetime import timedelta

class Settings(BaseSettings):
    JWT_SECRET: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REDIS_HOST: str 
    REDIS_PORT: int
    REDIS_DB: int
    ALLOWED_ORIGINS: List[str]
    DATABASE_URL: str
    MAILERSEND_API_KEY: str
    MAILERSEND_BASE_URL: str
    EMAIL_FROM: str

    class Config: # Tells pydantic where to look for env variables
        env_file = '.env' # No need for dotenv at all. Uninstal it

    @property # Turns a method into an attribute. Now settings.acceess_token_expire instead of settings.access_token_expire()
    def access_token_expire(self) -> timedelta:
        return timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)

settings = Settings()