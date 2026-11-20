"""Content service: generates content, PDF, and saves everything to DB."""

import json
import logging
import os
from datetime import datetime, date
from pathlib import Path

from sqlalchemy import select
from backend.content_generation.content_generator import ContentGenerator
from backend.pdf_generator.pdf_creator import PDFCreator
from backend.services.word_service import WordCreator
from backend.database.db_manager import get_session
from backend.database.models import Newsletter, ToolRecord, PublishedTool, NewsletterStatus
from backend.config.settings import settings

logger = logging.getLogger(__name__)


class ContentService:
    """Orchestrates content generation → PDF → DB persistence."""

    def __init__(self):
        self.generator = ContentGenerator()
        self.pdf_creator = PDFCreator()
        self.word_creator = WordCreator()

    async def get_next_issue_number(self) -> int:
        """Return the next sequential issue number."""
        try:
            async with get_session() as session:
                from sqlalchemy import func
                result = await session.execute(
                    select(func.max(Newsletter.issue_number))
                )
                max_issue = result.scalar()
                return (max_issue or 0) + 1
        except Exception:
            return 1

    async def run_content_pipeline(
        self,
        tools_research: list[dict],
        issue_number: int | None = None,
        template_name: str = "classic",
        custom_focus: str | None = None,
        pages_per_tool: int = 1,
    ) -> dict:
        """
        Full pipeline: generate content for all tools → render HTML → PDF → save.

        Args:
            tools_research: list of tool dicts with research_data
            issue_number: override issue number (auto-detected if None)
            template_name: "classic" | "modern"
            custom_focus: optional user focus/topic instruction
            pages_per_tool: 1 (spotlight) or 2 (deep-dive dossier)

        Returns:
            dict with pdf_path, json_path, newsletter_id, tools
        """
        if issue_number is None:
            issue_number = await self.get_next_issue_number()

        today = date.today()
        week_num = today.isocalendar()[1]
        year = today.year
        week_label = f"Week {week_num}, {year}"
        pub_date = today.strftime("%d %B %Y")

        issue_info = {
            "issue_number": issue_number,
            "week_label": week_label,
            "pub_date": pub_date,
            "title": settings.hal_newsletter_title,
            "pages_per_tool": pages_per_tool,
        }

        # 1. Generate content for each tool
        tools_content = []
        for idx, tool in enumerate(tools_research, start=1):
            logger.info("Generating content for tool %d: %s", idx, tool.get("name"))
            try:
                content = await self.generator.generate_tool_content(tool, custom_focus=custom_focus)
            except Exception as exc:
                logger.warning("Gemini generation failed for %r: %s — using structured fallback", tool.get("name"), exc)
                content = self.generator._validate_and_patch({
                    "name": tool.get("name", "AI Tool"),
                    "category": tool.get("category", "Workplace Productivity"),
                    "overview": tool.get("description", f"{tool.get('name')} is an intuitive AI assistant designed to streamline everyday workflows."),
                    "key_features": [
                        f"Streamlines routine {tool.get('category', 'technical')} workflows",
                        "Intuitive user interface and rapid setup",
                        "Simplifies reporting, documentation, and data coordination"
                    ],
                    "how_it_works": f"{tool.get('name')} uses intelligent models to automate routine tasks, structure findings, and enhance team productivity.",
                    "practical_applications": "Automates routine tasks, accelerates research, and assists in drafting reports.",
                    "hal_use_case": f"Employees across engineering, operations, and administration can leverage {tool.get('name')} to summarize technical guidelines and streamline workflow tracking.",
                    "hal_example_workflow": "Summarizing vendor equipment guidelines into a standardized inspection checklist.",
                    "sample_prompt": f"Review this technical summary, identify key action items for the team, and format the findings into a clean 3-point checklist.",
                    "website": tool.get("website", ""),
                    "pricing_tier": tool.get("pricing_tier", "Freemium"),
                    "pricing_details": tool.get("pricing_details", "Visit website for current pricing details."),
                    "security_note": "⚠ Do not upload classified, proprietary, or project-sensitive company data to external AI platforms. — HAL IT Security"
                }, tool)
            content["tool_number"] = idx
            tools_content.append(content)

        if not tools_content:
            raise RuntimeError("No tool content generated — aborting.")

        # 2. Build output paths
        output_dir = Path(settings.newsletter_output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        safe_date = today.strftime("%Y%m%d")
        base_name = f"HAL_AI_Tools_Weekly_Issue{issue_number:02d}_{safe_date}"
        pdf_path = str(output_dir / f"{base_name}.pdf")
        docx_path = str(output_dir / f"{base_name}.docx")
        json_path = str(output_dir / f"{base_name}.json")

        # 3. Generate PDF
        logger.info("Generating PDF: %s (template: %s)", pdf_path, template_name)
        await self.pdf_creator.generate_pdf(tools_content, issue_info, pdf_path, template_name=template_name)

        # 3b. Generate Word (.docx) document
        try:
            logger.info("Generating Word document: %s", docx_path)
            self.word_creator.generate_docx(tools_content, issue_info, docx_path)
        except Exception as docx_err:
            logger.error("Failed to generate docx document: %s", docx_err, exc_info=True)

        # 4. Save JSON data
        payload = {"issue_info": issue_info, "tools": tools_content, "template_name": template_name}
        Path(json_path).write_text(json.dumps(payload, indent=2), encoding="utf-8")

        # 5. Persist to database
        newsletter_id = await self._save_to_db(
            issue_info, tools_content, tools_research, pdf_path, json_path, template_name=template_name
        )

        logger.info("Pipeline complete. Newsletter ID: %d", newsletter_id)
        return {
            "newsletter_id": newsletter_id,
            "pdf_path": pdf_path,
            "docx_path": docx_path,
            "json_path": json_path,
            "tools": tools_content,
            "issue_info": issue_info,
        }

    async def _save_to_db(
        self,
        issue_info: dict,
        tools_content: list,
        tools_research: list,
        pdf_path: str,
        json_path: str,
        template_name: str = "classic",
    ) -> int:
        """Save newsletter and tool records to SQLite."""
        async with get_session() as session:
            # Create Newsletter record
            newsletter = Newsletter(
                issue_number=issue_info["issue_number"],
                week_label=issue_info["week_label"],
                pub_date=issue_info["pub_date"],
                pdf_path=pdf_path,
                json_path=json_path,
                template_name=template_name,
                status=NewsletterStatus.DRAFT,
            )
            session.add(newsletter)
            await session.flush()  # get newsletter.id

            # Create ToolRecord entries
            research_map = {t.get("name", "").lower(): t for t in tools_research}
            for content in tools_content:
                name_lower = content.get("name", "").lower()
                research = research_map.get(name_lower, {})
                tool_rec = ToolRecord(
                    newsletter_id=newsletter.id,
                    tool_number=content.get("tool_number", 1),
                    name=content.get("name", ""),
                    website=content.get("website", ""),
                    category=content.get("category", ""),
                    content_json=json.dumps(content),
                    is_verified=research.get("is_verified", False),
                )
                session.add(tool_rec)

                # Mark as published (dedup)
                pub = PublishedTool(
                    tool_name=content.get("name", ""),
                    website=content.get("website", ""),
                    published_week=issue_info["week_label"],
                )
                session.add(pub)

            return newsletter.id
