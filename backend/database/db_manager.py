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

from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

# ---------------------------------------------------------------------------
# Engine & session factory
# ---------------------------------------------------------------------------
def _normalize_db_url_and_args(raw_url: str) -> tuple[str, dict]:
    """Normalize PostgreSQL / Neon connection strings for asyncpg."""
    url = raw_url
    connect_args = {}

    if url.startswith("postgres://"):
        url = "postgresql+asyncpg://" + url[len("postgres://"):]
    elif url.startswith("postgresql://") and not url.startswith("postgresql+"):
        url = "postgresql+asyncpg://" + url[len("postgresql://"):]

    if "postgresql" in url or "postgres" in url:
        parsed = urlparse(url)
        # Strip all query parameters (e.g. sslmode, channel_binding) as asyncpg does not accept them via URL query
        url = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            "",
            "",
            ""
        ))
        # Enforce secure SSL for cloud PostgreSQL (like Neon)
        connect_args["ssl"] = "require"

    elif "sqlite" in url:
        connect_args["check_same_thread"] = False

    return url, connect_args


DATABASE_URL = "sqlite+aiosqlite:///./newsletter.db"
connect_args = {"check_same_thread": False}

try:
    from backend.config.settings import settings
    DATABASE_URL, connect_args = _normalize_db_url_and_args(settings.database_url)
except Exception:
    pass

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
