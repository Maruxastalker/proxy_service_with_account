from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import List
import json
import os


class Settings(BaseSettings):
    app_name: str = "Proxy Service"
    debug: bool = True
    secret_key: str = "change-me-in-production"
    
    database_url: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/proxy_db")
    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    
    jwt_secret_key: str = "jwt-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 15
    
    smtp_host: str = os.getenv("SMTP_HOST", "sandbox.smtp.mailtrap.io")
    smtp_port: int = int(os.getenv("SMTP_PORT", "2525"))
    smtp_username: str = os.getenv("SMTP_USERNAME", "4f3c5cde3204a3")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "3f517499a551cb")
    smtp_from_email: str = os.getenv("SMTP_FROM_EMAIL", "belehow.m.564717649@gmail.com")
    
    cors_origins: str = os.getenv("CORS_ORIGINS", '["http://localhost", "http://localhost:80"]')
    
    @property
    def cors_origins_list(self) -> List[str]:
        return json.loads(self.cors_origins)
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


settings = Settings()