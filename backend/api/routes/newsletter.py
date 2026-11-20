"""FastAPI router for newsletter generation and management."""

import json
import logging
from pathlib import Path
from pydantic import BaseModel

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.database.db_manager import get_session
from backend.database.models import Newsletter, ToolRecord, NewsletterStatus, PublishedTool
from backend.services.research_service import ResearchService
from backend.services.content_service import ContentService
from backend.content_generation.content_generator import ContentGenerator
from backend.pdf_generator.pdf_creator import PDFCreator
from backend.template_engine.html_renderer import HTMLRenderer
from backend.services.word_service import WordCreator
from backend.config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Newsletter"])

research_service = ResearchService()
content_service = ContentService()

# ---------------------------------------------------------------------------
# Background task state (tracked in-memory for live UI status updates)
# ---------------------------------------------------------------------------
_task_status: dict = {
    "status": "idle",       # "idle" | "running" | "complete" | "error"
    "step": None,           # "discovering" | "researching" | "verifying" | "generating" | "creating_pdf"
    "message": "",
    "newsletter_id": None,
    "newsletter": None,
    "tools": [],
    "error": None,
}


class GeneratePayload(BaseModel):
    template: str | None = "modern"
    tool_count: int | None = 3
    pages_per_tool: int | None = 1
    generation_mode: str | None = "direct"  # "direct" | "custom"
    custom_prompt: str | None = None


async def _run_full_pipeline(
    template_name: str = "modern",
    tool_count: int = 3,
    pages_per_tool: int = 1,
    generation_mode: str = "direct",
    custom_prompt: str | None = None,
):
    """Background task: research → content → PDF → DB."""
    global _task_status
    _task_status["status"] = "running"
    _task_status["error"] = None
    _task_status["tools"] = []
    _task_status["newsletter"] = None
    _task_status["template"] = template_name

    count = max(1, min(int(tool_count or 3), 5))
    ppt = max(1, min(int(pages_per_tool or 1), 2))
    total_pages = count * ppt
    focus = custom_prompt.strip() if (generation_mode == "custom" and custom_prompt) else None

    try:
        # Step 1: Discovering
        _task_status["step"] = "discovering"
        mode_label = f" (Focus: '{focus[:30]}...')" if focus else ""
        _task_status["message"] = f"Discovering {count} AI tools across the web{mode_label}..."
        logger.info(_task_status["message"])
        
        # We run discovery and research
        exclude_names = await research_service.get_published_tool_names()
        discovered = await research_service.researcher.discover_tools(
            count=count,
            exclude_names=exclude_names,
            custom_prompt=focus,
        )
        
        # Step 2: Researching
        _task_status["step"] = "researching"
        _task_status["message"] = f"Researching features and pricing for {len(discovered)} tools..."
        logger.info(_task_status["message"])
        
        researched = []
        for tool in discovered:
            try:
                data = await research_service.researcher.research_tool(tool["name"], tool.get("website", ""))
                data["category"] = tool.get("category", "AI Tool")
                data["description"] = tool.get("description", "")
                researched.append(data)
            except Exception as e:
                logger.warning("Research error for %s: %s", tool.get("name"), e)
                data = tool.copy()
                data["research_data"] = tool.get("description", "Workplace productivity AI tool.")
                researched.append(data)

        # Step 3: Verifying
        _task_status["step"] = "verifying"
        _task_status["message"] = "Verifying live availability and official websites..."
        logger.info(_task_status["message"])
        
        verified = []
        for tool in researched:
            v = await research_service.verifier.verify_tool(tool.copy())
            verified.append(v)

        # Step 4: Generating Content
        _task_status["step"] = "generating"
        _task_status["message"] = "Generating structured plain-English content via Gemini..."
        logger.info(_task_status["message"])

        # Step 5: Creating PDF & saving to DB
        _task_status["step"] = "creating_pdf"
        _task_status["message"] = f"Compiling {total_pages}-page A4 PDF ({count} tools × {ppt} pg) and QR codes..."
        logger.info(_task_status["message"])
        
        result = await content_service.run_content_pipeline(
            verified,
            template_name=template_name,
            custom_focus=focus,
            pages_per_tool=ppt,
        )

        _task_status["status"] = "complete"
        _task_status["step"] = None
        _task_status["message"] = "Newsletter generated successfully!"
        _task_status["newsletter_id"] = result["newsletter_id"]
        _task_status["newsletter"] = result["issue_info"]
        _task_status["tools"] = result["tools"]
        logger.info("Newsletter generation complete: ID %d", result["newsletter_id"])

    except Exception as exc:
        logger.error("Pipeline failed: %s", exc, exc_info=True)
        _task_status["status"] = "error"
        _task_status["step"] = None
        _task_status["error"] = str(exc)
        _task_status["message"] = f"Generation failed: {exc}"


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/generate")
async def generate_newsletter(
    background_tasks: BackgroundTasks,
    template: str | None = None,
    payload: GeneratePayload | None = None,
):
    """Trigger a full newsletter generation workflow in the background."""
    selected_template = "modern"
    tool_count = 3
    pages_per_tool = 1
    generation_mode = "direct"
    custom_prompt = None

    if payload:
        if payload.template:
            selected_template = payload.template
        if payload.tool_count:
            tool_count = payload.tool_count
        if payload.pages_per_tool:
            pages_per_tool = payload.pages_per_tool
        if payload.generation_mode:
            generation_mode = payload.generation_mode
        if payload.custom_prompt:
            custom_prompt = payload.custom_prompt
    elif template:
        selected_template = template

    if _task_status["status"] == "running":
        return {
            "status": "already_running",
            "id": "current",
            "newsletter_id": "current",
            "template": selected_template,
            "message": "A generation task is already in progress.",
        }

    background_tasks.add_task(
        _run_full_pipeline,
        template_name=selected_template,
        tool_count=tool_count,
        pages_per_tool=pages_per_tool,
        generation_mode=generation_mode,
        custom_prompt=custom_prompt,
    )
    _task_status["status"] = "running"
    _task_status["step"] = "discovering"
    _task_status["template"] = selected_template
    total_pgs = tool_count * pages_per_tool
    _task_status["message"] = f"Newsletter generation started ({tool_count} tools, {total_pgs} total pages, mode: {generation_mode})..."
    return {
        "status": "started",
        "id": "current",
        "newsletter_id": "current",
        "template": selected_template,
        "tool_count": tool_count,
        "pages_per_tool": pages_per_tool,
        "total_pages": total_pgs,
        "generation_mode": generation_mode,
        "message": f"Generation initiated ({tool_count} tools × {pages_per_tool} page(s), '{selected_template}' template).",
    }


@router.get("/generate/status")
@router.get("/status")
@router.get("/{newsletter_id}/status")
async def generation_status(newsletter_id: str | None = None):
    """Poll the status of the current/last generation run."""
    return _task_status


@router.get("/list")
async def list_newsletters():
    """Return all past newsletters in reverse chronological order."""
    async with get_session() as session:
        result = await session.execute(
            select(Newsletter)
            .options(selectinload(Newsletter.tools))
            .order_by(Newsletter.created_at.desc())
        )
        newsletters = result.scalars().all()
        data = [n.to_dict() for n in newsletters]
        return {"newsletters": data, "count": len(data)}


@router.get("/{newsletter_id}")
async def get_newsletter(newsletter_id: int):
    """Return full details for a specific newsletter, including tools."""
    async with get_session() as session:
        result = await session.execute(
            select(Newsletter)
            .options(selectinload(Newsletter.tools))
            .where(Newsletter.id == newsletter_id)
        )
        newsletter = result.scalar_one_or_none()
        if not newsletter:
            raise HTTPException(status_code=404, detail="Newsletter not found.")
        return newsletter.to_dict()


@router.get("/{newsletter_id}/preview", response_class=HTMLResponse)
async def preview_newsletter(newsletter_id: int):
    """Return the rendered HTML for browser preview."""
    async with get_session() as session:
        result = await session.execute(
            select(Newsletter)
            .options(selectinload(Newsletter.tools))
            .where(Newsletter.id == newsletter_id)
        )
        newsletter = result.scalar_one_or_none()
        if not newsletter:
            raise HTTPException(status_code=404, detail="Newsletter not found.")

    if newsletter.pdf_path:
        html_path = newsletter.pdf_path.replace(".pdf", ".html")
        if Path(html_path).exists():
            return Path(html_path).read_text(encoding="utf-8")

    # On-demand render from database tools
    tools_data = [t.to_dict()["content"] for t in newsletter.tools]
    if tools_data:
        renderer = HTMLRenderer()
        issue_info = {
            "issue_number": newsletter.issue_number,
            "week_label": newsletter.week_label,
            "pub_date": newsletter.pub_date,
            "title": settings.hal_newsletter_title,
            "pages_per_tool": getattr(newsletter, "pages_per_tool", 1) or 1,
        }
        return renderer.render_newsletter(tools_data, issue_info, template_name=newsletter.template_name or "modern")

    raise HTTPException(status_code=404, detail="Preview HTML not available.")


@router.put("/{newsletter_id}/tool/{tool_num}")
async def update_tool(newsletter_id: int, tool_num: int, update: dict):
    """Update editable content for a specific tool in a newsletter."""
    async with get_session() as session:
        result = await session.execute(
            select(ToolRecord).where(
                ToolRecord.newsletter_id == newsletter_id,
                ToolRecord.tool_number == tool_num,
            )
        )
        tool_rec = result.scalar_one_or_none()
        if not tool_rec:
            raise HTTPException(status_code=404, detail="Tool not found.")

        content = json.loads(tool_rec.content_json) if tool_rec.content_json else {}
        content.update(update)
        tool_rec.content_json = json.dumps(content)
        if "name" in update:
            tool_rec.name = update["name"]
        if "category" in update:
            tool_rec.category = update["category"]
        if "website" in update:
            tool_rec.website = update["website"]

        # Also re-render the HTML & PDF
        nl_result = await session.execute(
            select(Newsletter)
            .options(selectinload(Newsletter.tools))
            .where(Newsletter.id == newsletter_id)
        )
        newsletter = nl_result.scalar_one_or_none()
        if newsletter and newsletter.pdf_path:
            tools_data = [t.to_dict()["content"] for t in newsletter.tools]
            issue_info = {
                "issue_number": newsletter.issue_number,
                "week_label": newsletter.week_label,
                "pub_date": newsletter.pub_date,
                "title": settings.hal_newsletter_title,
            }
            pdf_creator = PDFCreator()
            tpl = getattr(newsletter, "template_name", "classic") or "classic"
            await pdf_creator.generate_pdf(tools_data, issue_info, newsletter.pdf_path, template_name=tpl)

    return {"status": "updated", "tool_number": tool_num}


@router.post("/{newsletter_id}/regenerate-tool/{tool_num}")
async def regenerate_tool(newsletter_id: int, tool_num: int):
    """Regenerate content for a single tool and update the PDF."""
    async with get_session() as session:
        result = await session.execute(
            select(ToolRecord).where(
                ToolRecord.newsletter_id == newsletter_id,
                ToolRecord.tool_number == tool_num,
            )
        )
        tool_rec = result.scalar_one_or_none()
        if not tool_rec:
            raise HTTPException(status_code=404, detail="Tool not found.")

        old_content = json.loads(tool_rec.content_json) if tool_rec.content_json else {}

    generator = ContentGenerator()
    new_content = await generator.generate_tool_content({
        "name": tool_rec.name,
        "category": tool_rec.category,
        "website": tool_rec.website,
        "research_data": old_content.get("research_data", ""),
    })
    new_content["tool_number"] = tool_num

    async with get_session() as session:
        result = await session.execute(
            select(ToolRecord).where(
                ToolRecord.newsletter_id == newsletter_id,
                ToolRecord.tool_number == tool_num,
            )
        )
        tool_rec = result.scalar_one_or_none()
        if tool_rec:
            tool_rec.content_json = json.dumps(new_content)

        nl_result = await session.execute(
            select(Newsletter)
            .options(selectinload(Newsletter.tools))
            .where(Newsletter.id == newsletter_id)
        )
        newsletter = nl_result.scalar_one_or_none()
        if newsletter and newsletter.pdf_path:
            tools_data = [t.to_dict()["content"] for t in newsletter.tools]
            issue_info = {
                "issue_number": newsletter.issue_number,
                "week_label": newsletter.week_label,
                "pub_date": newsletter.pub_date,
                "title": settings.hal_newsletter_title,
            }
            pdf_creator = PDFCreator()
            tpl = getattr(newsletter, "template_name", "classic") or "classic"
            await pdf_creator.generate_pdf(tools_data, issue_info, newsletter.pdf_path, template_name=tpl)

    return {"status": "regenerated", "tool": new_content}


@router.get("/{newsletter_id}/download")
async def download_newsletter(newsletter_id: int):
    """Stream the PDF file as a download (regenerates on demand if file was purged)."""
    async with get_session() as session:
        result = await session.execute(
            select(Newsletter)
            .options(selectinload(Newsletter.tools))
            .where(Newsletter.id == newsletter_id)
        )
        newsletter = result.scalar_one_or_none()
        if not newsletter:
            raise HTTPException(status_code=404, detail="Newsletter not found.")

    output_dir = Path(settings.newsletter_output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = newsletter.pdf_path

    # If pdf_path is missing or does not exist on disk, render on the fly from DB tools
    if not pdf_path or not Path(pdf_path).exists():
        safe_date = (newsletter.pub_date or "latest").replace(" ", "_")
        pdf_path = str(output_dir / f"HAL_AI_Tools_Weekly_Issue{newsletter.issue_number:02d}_{safe_date}.pdf")
        
        if not Path(pdf_path).exists():
            tools_data = [t.to_dict()["content"] for t in newsletter.tools]
            if not tools_data and newsletter.json_path and Path(newsletter.json_path).exists():
                try:
                    data = json.loads(Path(newsletter.json_path).read_text(encoding="utf-8"))
                    tools_data = data.get("tools", [])
                except Exception:
                    tools_data = []

            if not tools_data:
                raise HTTPException(status_code=404, detail="Newsletter content could not be found for PDF generation.")

            issue_info = {
                "issue_number": newsletter.issue_number,
                "week_label": newsletter.week_label,
                "pub_date": newsletter.pub_date,
                "title": settings.hal_newsletter_title,
                "pages_per_tool": getattr(newsletter, "pages_per_tool", 1) or 1,
            }
            pdf_creator = PDFCreator()
            tpl = getattr(newsletter, "template_name", "modern") or "modern"
            await pdf_creator.generate_pdf(tools_data, issue_info, pdf_path, template_name=tpl)

    filename = Path(pdf_path).name
    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=filename,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{newsletter_id}/download-word")
async def download_newsletter_word(newsletter_id: int):
    """Stream the newsletter as a styled Microsoft Word (.docx) document."""
    async with get_session() as session:
        result = await session.execute(
            select(Newsletter)
            .options(selectinload(Newsletter.tools))
            .where(Newsletter.id == newsletter_id)
        )
        newsletter = result.scalar_one_or_none()
        if not newsletter:
            raise HTTPException(status_code=404, detail="Newsletter not found.")

    output_dir = Path(settings.newsletter_output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_date = (newsletter.pub_date or "latest").replace(" ", "_")
    docx_path = str(output_dir / f"HAL_AI_Tools_Weekly_Issue{newsletter.issue_number:02d}_{safe_date}.docx")

    # If docx does not already exist on disk, generate it on demand from JSON or DB tools
    if not Path(docx_path).exists():
        tools_data = [t.to_dict()["content"] for t in newsletter.tools]
        if not tools_data and newsletter.json_path and Path(newsletter.json_path).exists():
            try:
                data = json.loads(Path(newsletter.json_path).read_text(encoding="utf-8"))
                tools_data = data.get("tools", [])
            except Exception:
                tools_data = []

        if not tools_data:
            raise HTTPException(status_code=404, detail="Newsletter content could not be retrieved for Word export.")

        issue_info = {
            "issue_number": newsletter.issue_number,
            "week_label": newsletter.week_label,
            "pub_date": newsletter.pub_date,
            "title": settings.hal_newsletter_title,
            "pages_per_tool": getattr(newsletter, "pages_per_tool", 1) or 1,
        }

        wc = WordCreator()
        try:
            wc.generate_docx(tools_data, issue_info, docx_path)
        except Exception as exc:
            logger.error("Failed to generate Word document for Issue %d: %s", newsletter_id, exc)
            raise HTTPException(status_code=500, detail=f"Word generation failed: {exc}")

    filename = Path(docx_path).name
    return FileResponse(
        path=docx_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=filename,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.put("/{newsletter_id}/approve")
async def approve_newsletter(newsletter_id: int):
    """Mark a newsletter as approved."""
    async with get_session() as session:
        result = await session.execute(
            select(Newsletter).where(Newsletter.id == newsletter_id)
        )
        newsletter = result.scalar_one_or_none()
        if not newsletter:
            raise HTTPException(status_code=404, detail="Newsletter not found.")
        newsletter.status = NewsletterStatus.APPROVED

    return {"status": "approved", "newsletter_id": newsletter_id}
