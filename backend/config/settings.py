"""Application settings loaded from config/.env via pydantic-settings."""

from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # AI / Search
    gemini_api_key: str = ""
    search_api_key: str = ""
    search_engine: str = "duckduckgo"

    # Storage
    newsletter_output_dir: str = "generated_newsletters"
    database_url: str = "sqlite+aiosqlite:///./newsletter.db"

    # Branding
    hal_newsletter_title: str = "HAL AI Tools Weekly"

    # Email
    admin_email: str = ""
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""

    # App
    base_url: str = "http://localhost:8000"
    templates_dir: str = "templates"

    class Config:
        env_file = "config/.env"
        env_file_encoding = "utf-8"


settings = Settings()
