"""Settings API routes with persistent .env storage."""

from pathlib import Path
import re
from fastapi import APIRouter
from pydantic import BaseModel
from backend.config.settings import settings
import google.generativeai as genai

router = APIRouter(tags=["Settings"])

ENV_PATH = Path("config/.env")


def save_to_env(updates: dict):
    """Update key-value pairs in config/.env file."""
    ENV_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not ENV_PATH.exists():
        if Path("config/.env.example").exists():
            content = Path("config/.env.example").read_text(encoding="utf-8")
        else:
            content = ""
    else:
        content = ENV_PATH.read_text(encoding="utf-8")

    lines = content.splitlines()
    new_lines = []
    seen = set()

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            new_lines.append(line)
            continue
        if "=" in line:
            key, val = line.split("=", 1)
            key = key.strip()
            if key in updates:
                new_lines.append(f"{key}={updates[key]}")
                seen.add(key)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    # Append any keys that weren't in the file
    for key, val in updates.items():
        if key not in seen:
            new_lines.append(f"{key}={val}")

    ENV_PATH.write_text("\n".join(new_lines) + "\n", encoding="utf-8")


class SettingsResponse(BaseModel):
    search_engine: str
    newsletter_output_dir: str
    hal_newsletter_title: str
    admin_email: str
    smtp_host: str
    smtp_port: int
    smtp_user: str
    base_url: str
    templates_dir: str
    gemini_api_key: str
    search_api_key: str
    gemini_configured: bool
    search_api_configured: bool


class SettingsUpdate(BaseModel):
    gemini_api_key: str | None = None
    search_api_key: str | None = None
    search_engine: str | None = None
    newsletter_output_dir: str | None = None
    hal_newsletter_title: str | None = None
    admin_email: str | None = None
    smtp_host: str | None = None
    smtp_port: int | str | None = None
    smtp_user: str | None = None
    smtp_password: str | None = None
    base_url: str | None = None


@router.get("", response_model=SettingsResponse)
async def get_settings():
    """Return current app configuration."""
    has_gemini = bool(settings.gemini_api_key and not settings.gemini_api_key.startswith("your_"))
    has_search = bool(settings.search_api_key and not settings.search_api_key.startswith("your_"))

    # Return partially masked key if present, so UI shows something is configured
    masked_gemini = ""
    if has_gemini:
        k = settings.gemini_api_key
        masked_gemini = k[:4] + "••••••••" + k[-4:] if len(k) > 10 else "••••••••"

    masked_search = ""
    if has_search:
        k = settings.search_api_key
        masked_search = k[:3] + "••••••••" + k[-3:] if len(k) > 8 else "••••••••"

    return SettingsResponse(
        search_engine=settings.search_engine,
        newsletter_output_dir=settings.newsletter_output_dir,
        hal_newsletter_title=settings.hal_newsletter_title,
        admin_email=settings.admin_email,
        smtp_host=settings.smtp_host,
        smtp_port=int(settings.smtp_port or 587),
        smtp_user=settings.smtp_user,
        base_url=settings.base_url,
        templates_dir=settings.templates_dir,
        gemini_api_key=masked_gemini,
        search_api_key=masked_search,
        gemini_configured=has_gemini,
        search_api_configured=has_search,
    )


@router.put("")
async def update_settings(update: SettingsUpdate):
    """Update settings and persist to config/.env."""
    env_updates = {}

    if update.gemini_api_key is not None and not update.gemini_api_key.startswith("••"):
        key = update.gemini_api_key.strip()
        if key:
            settings.gemini_api_key = key
            env_updates["GEMINI_API_KEY"] = key
            try:
                genai.configure(api_key=key)
            except Exception:
                pass

    if update.search_api_key is not None and not update.search_api_key.startswith("••"):
        key = update.search_api_key.strip()
        settings.search_api_key = key
        env_updates["SEARCH_API_KEY"] = key

    if update.search_engine is not None:
        settings.search_engine = update.search_engine
        env_updates["SEARCH_ENGINE"] = update.search_engine

    if update.newsletter_output_dir is not None:
        settings.newsletter_output_dir = update.newsletter_output_dir
        env_updates["NEWSLETTER_OUTPUT_DIR"] = update.newsletter_output_dir

    if update.hal_newsletter_title is not None:
        settings.hal_newsletter_title = update.hal_newsletter_title
        env_updates["HAL_NEWSLETTER_TITLE"] = update.hal_newsletter_title

    if update.admin_email is not None:
        settings.admin_email = update.admin_email
        env_updates["ADMIN_EMAIL"] = update.admin_email

    if update.base_url is not None:
        settings.base_url = update.base_url
        env_updates["BASE_URL"] = update.base_url

    if update.smtp_host is not None:
        settings.smtp_host = update.smtp_host
        env_updates["SMTP_HOST"] = update.smtp_host

    if update.smtp_port is not None:
        settings.smtp_port = int(update.smtp_port)
        env_updates["SMTP_PORT"] = str(update.smtp_port)

    if update.smtp_user is not None:
        settings.smtp_user = update.smtp_user
        env_updates["SMTP_USER"] = update.smtp_user

    if update.smtp_password is not None and not update.smtp_password.startswith("••"):
        settings.smtp_password = update.smtp_password
        env_updates["SMTP_PASSWORD"] = update.smtp_password

    if env_updates:
        save_to_env(env_updates)

    return {
        "status": "updated",
        "gemini_configured": bool(settings.gemini_api_key),
        "search_api_configured": bool(settings.search_api_key),
    }
