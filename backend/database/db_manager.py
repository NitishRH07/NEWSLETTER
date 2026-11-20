"""Async SQLite database manager using SQLAlchemy + aiosqlite."""

import asyncio
import sys
from pathlib import Path

# Ensure project root is in sys.path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from backend.database.models import Base

# ---------------------------------------------------------------------------
# Engine & session factory
# ---------------------------------------------------------------------------
def _normalize_db_url(url: str) -> str:
    """Normalize PostgreSQL / Neon connection strings for asyncpg."""
    if url.startswith("postgres://"):
        url = "postgresql+asyncpg://" + url[len("postgres://"):]
    elif url.startswith("postgresql://") and not url.startswith("postgresql+"):
        url = "postgresql+asyncpg://" + url[len("postgresql://"):]
    return url

DATABASE_URL = "sqlite+aiosqlite:///./newsletter.db"

try:
    from backend.config.settings import settings
    DATABASE_URL = _normalize_db_url(settings.database_url)
except Exception:
    pass

connect_args = {}
if "sqlite" in DATABASE_URL:
    connect_args["check_same_thread"] = False

async_engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    connect_args=connect_args,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

async def init_db() -> None:
    """Create all tables (safe to call multiple times — uses CREATE IF NOT EXISTS)."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("[DB] Tables initialised successfully.")


@asynccontextmanager
async def get_session():
    """Async context manager that yields a usable AsyncSession and commits/rolls back."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# FastAPI dependency variant (plain async generator for Depends())
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if "--init" in sys.argv or len(sys.argv) == 1:
        print("[DB] Initialising database …")
        asyncio.run(init_db())
        print("[DB] Done.")
    else:
        print("Usage: python -m backend.database.db_manager [--init]")
