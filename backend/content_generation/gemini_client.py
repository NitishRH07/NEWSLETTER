"""Gemini API client wrapper."""

import asyncio
import logging
import google.generativeai as genai
from backend.config.settings import settings

logger = logging.getLogger(__name__)

# Preferred models in priority order (flash-lite models have high free-tier quotas and low latency)
MODELS_TO_TRY = [
    "gemini-3.1-flash-lite",
    "gemini-3.1-flash-lite-preview",
    "gemini-3-flash-preview",
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-flash-latest",
]


class GeminiClient:
    """Thin async wrapper around the google-generativeai SDK."""

    def __init__(self):
        self.model = None
        self._current_model_name = None

    def _ensure_configured(self):
        if not settings.gemini_api_key or settings.gemini_api_key.startswith("your_"):
            raise ValueError(
                "Gemini API key is not configured. "
                "Please enter a valid GEMINI_API_KEY in the Settings page or in config/.env."
            )
        genai.configure(api_key=settings.gemini_api_key)

        if self.model is None:
            # Pick first available model
            for m in MODELS_TO_TRY:
                try:
                    self.model = genai.GenerativeModel(m)
                    self._current_model_name = m
                    break
                except Exception:
                    continue
            if self.model is None:
                self.model = genai.GenerativeModel("gemini-3.1-flash-lite")
                self._current_model_name = "gemini-3.1-flash-lite"

    async def generate(self, prompt: str) -> str:
        """Generate text from `prompt` using Gemini."""
        self._ensure_configured()
        loop = asyncio.get_event_loop()

        for m_name in [self._current_model_name] + [m for m in MODELS_TO_TRY if m != self._current_model_name]:
            try:
                model = genai.GenerativeModel(m_name)
                response = await loop.run_in_executor(
                    None,
                    lambda: model.generate_content(prompt, request_options={"timeout": 30})
                )
                if response and response.text:
                    self.model = model
                    self._current_model_name = m_name
                    logger.info("Successfully generated content with Gemini model: %s", m_name)
                    return response.text
            except Exception as exc:
                logger.warning("Gemini model %s failed: %s — trying next fallback", m_name, exc)
                continue

        raise RuntimeError("All Gemini models failed to generate content.")
