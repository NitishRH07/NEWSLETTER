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

def test_html_renderer():
    renderer = HTMLRenderer(str(project_root / "templates"))
    html = renderer.render_newsletter(
        tools=[TEST_TOOL],
        issue_info={
            "issue_number": 99,
            "week_label": "Week 01, 2026",
            "pub_date": "01 January 2026",
            "title": "HAL AI Tools Weekly"
        }
    )
    assert "HAL LOGO" in html
    assert "TestAI" in html
    assert "AI Testing Tool" in html
    assert "Page 01 of 1" in html

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
        output_path=out_pdf
    )
    assert Path(res).exists()
    assert Path(res).stat().st_size > 5000  # valid PDF
