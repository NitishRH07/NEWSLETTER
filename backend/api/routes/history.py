"""History API routes — list previously published tools."""

from fastapi import APIRouter
from sqlalchemy import select
from backend.database.db_manager import get_session
from backend.database.models import PublishedTool

router = APIRouter(tags=["History"])


@router.get("/tools")
async def list_published_tools():
    """Return all tools that have been published, for deduplication reference."""
    async with get_session() as session:
        result = await session.execute(
            select(PublishedTool).order_by(PublishedTool.created_at.desc())
        )
        tools = result.scalars().all()
        return [t.to_dict() for t in tools]
