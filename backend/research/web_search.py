"""Web search abstraction — DuckDuckGo (default) or SerpAPI (fallback)."""

import asyncio
import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)


class WebSearcher:
    """Thin async wrapper around DuckDuckGo / SerpAPI search."""

    def __init__(self, engine: str = "duckduckgo", serpapi_key: str = ""):
        self.engine = engine
        self.serpapi_key = serpapi_key

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def search(self, query: str, num_results: int = 5) -> list[dict]:
        """Return a list of {title, link, snippet} dicts."""
        try:
            if self.engine == "serpapi" and self.serpapi_key:
                return await asyncio.get_event_loop().run_in_executor(
                    None, self._serpapi_search, query, num_results
                )
            return await asyncio.get_event_loop().run_in_executor(
                None, self._ddg_search, query, num_results
            )
        except Exception as exc:
            logger.warning("Search failed for %r: %s — returning empty list", query, exc)
            return []

    # ------------------------------------------------------------------
    # Backends
    # ------------------------------------------------------------------

    def _ddg_search(self, query: str, num_results: int) -> list[dict]:
        from duckduckgo_search import DDGS

        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=num_results):
                results.append({
                    "title": r.get("title", ""),
                    "link": r.get("href", ""),
                    "snippet": r.get("body", ""),
                })
        return results

    def _serpapi_search(self, query: str, num_results: int) -> list[dict]:
        params = {
            "q": query,
            "api_key": self.serpapi_key,
            "num": num_results,
            "engine": "google",
        }
        resp = requests.get("https://serpapi.com/search", params=params, timeout=15)
        resp.raise_for_status()
        data: dict[str, Any] = resp.json()
        results = []
        for r in data.get("organic_results", [])[:num_results]:
            results.append({
                "title": r.get("title", ""),
                "link": r.get("link", ""),
                "snippet": r.get("snippet", ""),
            })
        return results
