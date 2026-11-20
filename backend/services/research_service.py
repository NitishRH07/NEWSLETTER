"""Research service: discovers, researches, and verifies AI tools per issue."""

import asyncio
import logging
from sqlalchemy import select
from backend.research.tool_researcher import ToolResearcher
from backend.research.verifier import ToolVerifier
from backend.database.db_manager import get_session
from backend.database.models import PublishedTool

logger = logging.getLogger(__name__)


class ResearchService:
    """High-level orchestrator for the tool discovery pipeline."""

    def __init__(self):
        self.researcher = ToolResearcher()
        self.verifier = ToolVerifier()

    async def get_published_tool_names(self) -> list[str]:
        """Return names of all previously published tools (for dedup)."""
        try:
            async with get_session() as session:
                result = await session.execute(select(PublishedTool.tool_name))
                return [row[0] for row in result.all()]
        except Exception as exc:
            logger.warning("Could not load published tools from DB: %s", exc)
            return []

    async def run_research_pipeline(self, count: int = 3, custom_prompt: str | None = None) -> list[dict]:
        """
        Full pipeline: discover → research → verify → return tool dicts.

        Args:
            count: Number of tools to discover and research (1, 2, or 3).
            custom_prompt: Optional custom instructions or topic focus.

        Returns:
            list of `count` verified tool dicts with research_data attached.
        """
        # 1. Load exclusion list
        exclude_names = await self.get_published_tool_names()
        logger.info("Excluding %d previously published tools.", len(exclude_names))

        # 2. Discover tools
        discovered = await self.researcher.discover_tools(
            count=count,
            exclude_names=exclude_names,
            custom_prompt=custom_prompt
        )
        logger.info("Discovered %d tools: %s", len(discovered), [t["name"] for t in discovered])

        # 3. Research each tool
        researched = []
        for tool in discovered:
            try:
                data = await self.researcher.research_tool(tool["name"], tool.get("website", ""))
                # Merge discovery metadata
                data["category"] = tool.get("category", "AI Tool")
                data["description"] = tool.get("description", "")
                researched.append(data)
            except Exception as exc:
                logger.error("Research failed for %r: %s", tool["name"], exc)
                data = tool.copy()
                data["research_data"] = tool.get("description", "Workplace productivity AI tool.")
                researched.append(data)

        # 4. Verify websites in parallel
        tasks = [self.verifier.verify_tool(tool.copy()) for tool in researched]
        verified = await asyncio.gather(*tasks, return_exceptions=True)
        verified = [v for v in verified if isinstance(v, dict)]

        logger.info("Verified %d tools.", len(verified))
        return verified[:count]
