"""Tool website verification helper."""

import logging
import httpx

logger = logging.getLogger(__name__)


class ToolVerifier:
    """Checks whether a tool's website is live and accessible."""

    async def verify_website(self, url: str) -> bool:
        """Return True if the URL responds with HTTP status < 400."""
        if not url:
            return False
        try:
            async with httpx.AsyncClient(
                follow_redirects=True,
                timeout=10.0,
                headers={"User-Agent": "Mozilla/5.0 (HAL Newsletter Bot)"},
            ) as client:
                # Try HEAD first (cheaper); fall back to GET if server rejects it
                try:
                    resp = await client.head(url)
                except httpx.RequestError:
                    resp = await client.get(url)
                return resp.status_code < 400
        except Exception as exc:
            logger.debug("Verification failed for %s: %s", url, exc)
            return False

    async def verify_tool(self, tool_data: dict) -> dict:
        """Add `is_verified` and `verification_note` fields to `tool_data`."""
        url = tool_data.get("website", "")
        is_live = await self.verify_website(url)
        tool_data["is_verified"] = is_live
        tool_data["verification_note"] = (
            "Website verified as live." if is_live
            else f"Could not reach {url!r} — may still be valid."
        )
        return tool_data
