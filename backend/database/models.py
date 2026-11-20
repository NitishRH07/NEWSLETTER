"""SQLAlchemy ORM models for the HAL Newsletter Generator."""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime,
    ForeignKey, Enum
)
from sqlalchemy.orm import relationship, DeclarativeBase
import enum


class Base(DeclarativeBase):
    pass


class NewsletterStatus(str, enum.Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    PUBLISHED = "published"


class Newsletter(Base):
    """Represents one weekly newsletter issue (3 tools → 1 PDF)."""
    __tablename__ = "newsletters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    issue_number = Column(Integer, nullable=False)
    week_label = Column(String(50), nullable=False)          # e.g. "Week 47, 2025"
    pub_date = Column(String(20), nullable=False)             # ISO date string
    pdf_path = Column(String(500), nullable=True)
    json_path = Column(String(500), nullable=True)
    template_name = Column(String(50), default="classic", nullable=True)
    status = Column(
        Enum(NewsletterStatus, native_enum=False),
        default=NewsletterStatus.DRAFT,
        nullable=False
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationship
    tools = relationship("ToolRecord", back_populates="newsletter", cascade="all, delete-orphan")

    def to_dict(self):
        tool_list = []
        try:
            if self.tools:
                tool_list = [t.to_dict() for t in self.tools]
        except Exception:
            pass
        return {
            "id": self.id,
            "issue_number": self.issue_number,
            "week_label": self.week_label,
            "pub_date": self.pub_date,
            "pdf_path": self.pdf_path,
            "json_path": self.json_path,
            "template_name": self.template_name or "classic",
            "status": self.status.value if self.status else "draft",
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "tools": tool_list,
        }


class ToolRecord(Base):
    """Stores individual AI tool data within a newsletter issue."""
    __tablename__ = "tool_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    newsletter_id = Column(Integer, ForeignKey("newsletters.id"), nullable=False)
    tool_number = Column(Integer, nullable=False)             # 1, 2, or 3
    name = Column(String(200), nullable=False)
    website = Column(String(500), nullable=True)
    category = Column(String(100), nullable=True)
    content_json = Column(Text, nullable=True)                # Full Gemini-generated JSON as string
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    newsletter = relationship("Newsletter", back_populates="tools")

    def to_dict(self):
        import json
        content = {}
        if self.content_json:
            try:
                content = json.loads(self.content_json)
            except Exception:
                content = {}
        return {
            "id": self.id,
            "newsletter_id": self.newsletter_id,
            "tool_number": self.tool_number,
            "name": self.name,
            "website": self.website,
            "category": self.category,
            "content": content,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class PublishedTool(Base):
    """Tracks previously published tools to avoid duplicates in future issues."""
    __tablename__ = "published_tools"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tool_name = Column(String(200), nullable=False)
    website = Column(String(500), nullable=True)
    published_week = Column(String(50), nullable=True)        # Week label
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "tool_name": self.tool_name,
            "website": self.website,
            "published_week": self.published_week,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
