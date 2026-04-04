from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import EmailStr
from typing import Literal
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    APP_NAME: str = "MyApp"
    APP_ENV: Literal["development", "production"] = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-me-in-production-at-least-32-chars"
    FRONTEND_URL: str = "http://localhost:3000"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/myapp"

    # Redis
    REDIS_URL: str = "redis://:redispassword@redis:6379/0"

    # Tokens
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    MFA_CHALLENGE_TOKEN_EXPIRE_MINUTES: int = 5

    # TOTP
    TOTP_ENCRYPTION_KEY: str = ""

    # Mail
    MAIL_PROVIDER: Literal["smtp", "sendgrid", "resend"] = "smtp"
    MAIL_FROM: str = "noreply@myapp.com"
    MAIL_FROM_NAME: str = "MyApp"
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 1025
    SMTP_USER: str = ""
    SMTP_PASS: str = ""
    SENDGRID_API_KEY: str = ""
    RESEND_API_KEY: str = ""

    # Superadmin seed
    SUPERADMIN_EMAIL: str = "admin@example.com"
    SUPERADMIN_PASSWORD: str = "Admin1234!"
    SUPERADMIN_FIRST_NAME: str = "Super"
    SUPERADMIN_LAST_NAME: str = "Admin"

    # Storage
    STORAGE_BACKEND: Literal["local", "s3"] = "local"
    STORAGE_PATH: str = "./uploads"
    S3_ENDPOINT_URL: str = ""
    S3_BUCKET_NAME: str = ""
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""
    S3_REGION: str = "us-east-1"
    S3_PUBLIC_URL: str = ""


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
