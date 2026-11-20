"""
Tests for content generation and validation logic.
"""
import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.content_generation.prompt_templates import TOOL_CONTENT_PROMPT
from backend.content_generation.content_generator import ContentGenerator

def test_prompt_template_formatting():
    prompt = TOOL_CONTENT_PROMPT.format(
        tool_name="SampleTool",
        category="AI Productivity",
        website="https://sample.ai",
        research_data="Key features include note taking and summary generation."
    )
    assert "SampleTool" in prompt
    assert "AI Productivity" in prompt
    assert "https://sample.ai" in prompt
    assert "HAL" in prompt
    assert "classified" in prompt

def test_json_parsing_and_fallback():
    cg = ContentGenerator()
    valid_json = '{"name": "Test", "category": "AI", "overview": "Desc", "key_features": ["f1", "f2", "f3"], "how_it_works": "works", "practical_applications": "apps", "hal_use_case": "hal", "sample_prompt": "prompt", "website": "https://test.ai", "pricing_tier": "Free", "security_note": "note"}'
    parsed = cg._parse_json(valid_json)
    assert parsed["name"] == "Test"
    assert len(parsed["key_features"]) == 3

    patched = cg._validate_and_patch(parsed, {"name": "Test", "website": "https://test.ai"})
    assert "website_display" in patched
    assert patched["website_display"] == "test.ai"
