"""Tests for Word (.docx) export generation."""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.services.word_service import WordCreator


def test_word_generation_creates_valid_file(tmp_path):
    output_docx = tmp_path / "test_newsletter.docx"
    creator = WordCreator()

    sample_tools = [
        {
            "tool_number": 1,
            "name": "Kite",
            "category": "AI Coding Assistant",
            "website": "https://kite.com",
            "pricing_tier": "Freemium",
            "overview": "Kite provides AI-powered code autocompletions directly inside your development environment.",
            "key_features": [
                "Local Line Autocomplete: Synthesizes multi-token completions based on local file context",
                "Side-Pane Documentation: Renders instant documentation and signature tooltips",
                "Local Execution: Analyzes files locally with minimal latency",
            ],
            "how_it_works_steps": [
                {"step": "01", "title": "IDE Integration", "description": "Install plugin into supported editor."},
                {"step": "02", "title": "Local Indexing", "description": "Indexes open workspace files."},
                {"step": "03", "title": "Inline Completion", "description": "Suggests completions as you type."},
            ],
            "hal_use_case": "Software teams can use Kite to write routine automation scripts and utility libraries.",
            "hal_example_workflow": "Accelerating data processing script development for telemetry verification.",
            "adaptive_workflow": {
                "mode_label": "IDE Shortcut & Automation Triggers",
                "primary_action": "Press Tab to accept autocomplete; Ctrl+Space to force suggest.",
                "guidance_tip": "Keep functions modular for highest autocomplete relevance.",
            },
            "at_a_glance": {
                "time_savings": "~4 to 6 hrs/week",
                "efficiency_gain": "Up to 35% faster",
                "target_teams": "Software & DevOps",
                "learning_curve": "Zero (Passive)",
            },
            "page_2_dossier": {
                "integration_architecture": {
                    "environment": "Local IDE plugin (VS Code, JetBrains)",
                    "computation_model": "Local GPU/CPU inference without external cloud transmission",
                    "supported_formats": "Python, JavaScript, Go, C++",
                    "setup_prerequisites": "Standard developer workspace with IDE permissions",
                },
                "case_study": {
                    "scenario_title": "Automated Parsing Script Development",
                    "context": "Engineers writing data validation scripts for equipment logs.",
                    "raw_input_sample": "def parse_inspection_log(file_path):",
                    "transformation_step": "Kite automatically completed file opening, exception handling, and regex parsing.",
                    "final_deliverable": "Fully validated test script in 5 minutes instead of 45 minutes.",
                },
                "governance_matrix": {
                    "permitted_data": ["Public APIs", "Unclassified utility scripts", "Standard open source libraries"],
                    "prohibited_data": ["Proprietary aerospace models", "Classified flight control algorithms", "ITAR technical manuals"],
                },
                "enterprise_faq": [
                    {"q": "Does Kite send code outside the local machine?", "a": "No, local engine processes files on-device."},
                    {"q": "Can it be used on air-gapped workstations?", "a": "Yes, offline installation bundles are available."},
                ],
            },
        }
    ]

    issue_info = {
        "issue_number": 99,
        "week_label": "Week 47, 2026",
        "pub_date": "20 November 2026",
        "title": "HAL AI Tools Weekly",
    }

    result_path = creator.generate_docx(sample_tools, issue_info, str(output_docx))
    assert Path(result_path).exists()
    assert Path(result_path).stat().st_size > 10000  # valid docx file
