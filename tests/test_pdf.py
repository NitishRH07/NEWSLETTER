"""
Tests for PDF creation and template rendering.
"""
import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pytest
import asyncio
from backend.template_engine.html_renderer import HTMLRenderer
from backend.pdf_generator.pdf_creator import PDFCreator

TEST_TOOL = {
    "name": "TestAI",
    "category": "AI Testing Tool",
    "overview": "A test tool overview for validation.",
    "key_features": ["Feature A", "Feature B", "Feature C"],
    "how_it_works": "Works via testing pipelines.",
    "practical_applications": "Used for automated quality checks.",
    "hal_use_case": "Could assist HAL software testing teams.",
    "sample_prompt": "Run automated test suite.",
    "website": "https://example.com",
    "website_display": "example.com",
    "pricing_tier": "Free",
    "pricing_details": "Free and open source.",
    "security_note": "Do not upload sensitive data."
}

TEST_GN3_TOOL = {
    "name": "DocuMate AI",
    "category": "Office Writing & Memos",
    "everyday_analogy": "Think of it like an autocorrect for complete office letters.",
    "overview": "DocuMate AI helps teams draft clean memos and checklists.",
    "what_it_does": "It drafts routine correspondence and summarizes meetings.",
    "key_features": [
        "Drafting: Fast memos",
        "Summaries: Quick notes",
        "Checklists: 1-click lists",
        "Sharing: Clean export",
        "Review: Complete employee control"
    ],
    "before_and_after": {
        "pain_before": "Hours of manual reformatting and retyping.",
        "relief_after": "Instant 60-second clean drafts."
    },
    "how_it_works_steps": [
        {"step": "01", "title": "Provide Material", "desc": "Drop in notes."},
        {"step": "02", "title": "Ask Plain Words", "desc": "Type what you need."},
        {"step": "03", "title": "Review & Use", "desc": "Copy the result."}
    ],
    "where_it_helps": [
        {"icon": "📋", "title": "Administration", "desc": "Draft memos."},
        {"icon": "📦", "title": "Stores", "desc": "Track items."},
        {"icon": "🔧", "title": "Maintenance", "desc": "Checklists."}
    ],
    "feature_snapshot": {
        "input_badge": "STEP 1: INPUT",
        "input_icon": "📄",
        "input_title": "Notes",
        "input_desc": "Messy text",
        "ai_step_badge": "STEP 2: ACTION",
        "ai_step_icon": "✨",
        "ai_step_title": "Ask in English",
        "ai_step_desc": "Summarize",
        "output_badge": "STEP 3: RESULT",
        "output_icon": "✅",
        "output_title": "Clean Memo",
        "output_desc": "Ready document",
        "key_advantage": "Saves hours every week."
    },
    "impact_metrics": {
        "time_saved": "~4 hrs/week",
        "key_metric": "70% faster",
        "learning_curve": "Zero"
    },
    "adaptive_workflow": {
        "standard_title": "60-SECOND QUICK TRYOUT",
        "standard_body": "Please summarize these notes into 3 bullets."
    },
    "website": "https://example.com",
    "website_display": "example.com",
    "pricing_tier": "Free",
    "pricing_details": "Free forever",
    "security_note": "Do not enter classified data."
}

def test_html_renderer_classic():
    renderer = HTMLRenderer(str(project_root / "templates"))
    html = renderer.render_newsletter(
        tools=[TEST_TOOL],
        issue_info={
            "issue_number": 99,
            "week_label": "Week 01, 2026",
            "pub_date": "01 January 2026",
            "title": "HAL AI Tools Weekly"
        },
        template_name="classic"
    )
    assert "HAL LOGO" in html
    assert "TestAI" in html
    assert "AI Testing Tool" in html
    assert "Page 01 of 1" in html

def test_html_renderer_gn3_hal():
    renderer = HTMLRenderer(str(project_root / "templates"))
    html = renderer.render_newsletter(
        tools=[TEST_GN3_TOOL],
        issue_info={
            "issue_number": 99,
            "week_label": "Week 01, 2026",
            "pub_date": "01 January 2026",
            "title": "HAL AI TOOLS WEEKLY"
        },
        template_name="gn3_hal"
    )
    assert "GN3-HAL EMPLOYEE EDITION" in html
    assert "DocuMate AI" in html
    assert "Everyday Analogy" in html or "How to Picture This Tool" in html
    assert "The Manual Way (Pain)" in html
    assert "With This Tool (Relief)" in html

@pytest.mark.asyncio
async def test_pdf_generation(tmp_path):
    creator = PDFCreator()
    out_pdf = str(tmp_path / "test_newsletter.pdf")
    res = await creator.generate_pdf(
        tools_data=[TEST_TOOL],
        issue_info={
            "issue_number": 99,
            "week_label": "Week 01, 2026",
            "pub_date": "01 January 2026",
            "title": "HAL AI Tools Weekly"
        },
        output_path=out_pdf,
        template_name="classic"
    )
    assert Path(res).exists()
    assert Path(res).stat().st_size > 5000  # valid PDF
