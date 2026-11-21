"""Gemini API client wrapper with multi-model fallback cascade."""

import asyncio
import logging
import google.generativeai as genai
from backend.config.settings import settings

logger = logging.getLogger(__name__)

# Preferred models in priority order for robust multi-model fallback cascade
MODELS_TO_TRY = [
    "gemini-2.5-flash",
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.1-flash-lite-preview",
    "gemini-3-flash-preview",
    "gemini-1.5-pro",
    "gemini-flash-latest",
]


class GeminiClient:
    """Thin async wrapper around the google-generativeai SDK with automatic model cascade."""

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
                self.model = genai.GenerativeModel("gemini-1.5-flash")
                self._current_model_name = "gemini-1.5-flash"

    async def generate(self, prompt: str) -> str:
        """
        Generate text from `prompt` using Gemini with automatic multi-model failover.
        Cycles through MODELS_TO_TRY on rate limits, quota issues, or API errors.
        """
        self._ensure_configured()
        loop = asyncio.get_event_loop()

        # Build prioritized candidate list starting with current model
        candidates = []
        if self._current_model_name:
            candidates.append(self._current_model_name)
        for m in MODELS_TO_TRY:
            if m not in candidates:
                candidates.append(m)

        last_error = None
        for m_name in candidates:
            try:
                logger.info("Attempting content generation with Gemini model: %s", m_name)
                model = genai.GenerativeModel(m_name)
                response = await loop.run_in_executor(
                    None,
                    lambda: model.generate_content(prompt, request_options={"timeout": 35})
                )
                if response and response.text:
                    self.model = model
                    self._current_model_name = m_name
                    logger.info("Successfully generated content with Gemini model: %s", m_name)
                    return response.text
            except Exception as exc:
                last_error = exc
                logger.warning("Gemini model %s encountered error: %s — cascading to next model", m_name, exc)
                continue

        raise RuntimeError(f"All Gemini models in fallback cascade failed. Last error: {last_error}")
