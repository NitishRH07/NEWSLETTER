"""
Sample data script — generates a sample newsletter PDF using 3 hardcoded AI
tools without requiring any API keys.

Usage:
    venv\Scripts\python backend\sample_data.py
"""

import asyncio
import sys
import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Make sure we can import backend modules from project root
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.pdf_generator.pdf_creator import PDFCreator

# ---------------------------------------------------------------------------
# Hardcoded tool data (realistic, based on public knowledge)
# ---------------------------------------------------------------------------

SAMPLE_TOOLS = [
    {
        "name": "Perplexity AI",
        "category": "AI Search & Research",
        "overview": (
            "Perplexity AI is an AI-powered answer engine that provides accurate, "
            "real-time answers to complex questions with cited sources. Unlike traditional "
            "search engines, it synthesises information across multiple sources into concise, "
            "readable summaries. It supports follow-up questions, file uploads, and deep research mode."
        ),
        "key_features": [
            "Real-time web search with cited, verifiable sources",
            "Deep Research mode for multi-step, in-depth reports",
            "File upload support for PDF/document Q&A",
        ],
        "how_it_works": (
            "Perplexity uses a retrieval-augmented generation (RAG) architecture, combining "
            "large language models with live web search. When a query is submitted, it retrieves "
            "relevant web pages in real time, then synthesises the content into a coherent answer "
            "with inline citations. Users can refine results through follow-up prompts."
        ),
        "practical_applications": (
            "Researchers use Perplexity to rapidly survey literature and compile annotated "
            "summaries. Business analysts rely on it for competitive intelligence and market "
            "research. Engineers use it to find up-to-date technical specifications, standards, "
            "and regulatory documents without manual web browsing."
        ),
        "hal_use_case": (
            "HAL engineers can use Perplexity AI to quickly survey global aerospace standards "
            "(MIL-SPEC, STANAG, ARP4754A) and retrieve the latest MRO best practices, "
            "reducing manual literature search time by 60–70%. It is particularly valuable "
            "for R&D teams tracking competitor aircraft programmes and emerging propulsion technologies."
        ),
        "sample_prompt": (
            "Summarise the latest revisions to ARP4761 and ARP4754A for safety assessment of "
            "civil aircraft systems, and highlight key differences from previous editions."
        ),
        "website": "https://www.perplexity.ai",
        "website_display": "perplexity.ai",
        "pricing_tier": "Freemium",
        "pricing_details": "Free tier available; Pro at $20/month with unlimited Deep Research.",
        "security_note": (
            "⚠ Do not upload classified, ITAR-controlled, or project-sensitive data to external "
            "AI platforms. Verify data handling policies before use. — HAL IT Security"
        ),
    },
    {
        "name": "Gamma.app",
        "category": "AI Presentation Generator",
        "overview": (
            "Gamma is an AI-powered presentation and document creation platform that transforms "
            "text prompts or outlines into polished, professional slides within seconds. "
            "It supports one-click redesign, interactive web publishing, and real-time collaboration, "
            "making it ideal for rapid deck creation without design expertise."
        ),
        "key_features": [
            "AI-generated slides from a text prompt or outline in under 60 seconds",
            "One-click theme and layout redesign across all slides",
            "Interactive web publishing with analytics and embed support",
        ],
        "how_it_works": (
            "Users input a topic or paste an outline; Gamma's AI selects an appropriate structure, "
            "generates slide content, and applies a cohesive visual theme automatically. "
            "The editor allows drag-and-drop customisation, media embedding, and style changes. "
            "Decks can be shared as interactive web pages or exported to PowerPoint/PDF."
        ),
        "practical_applications": (
            "Project managers use Gamma to create status reports and stakeholder briefings in minutes. "
            "Sales teams build tailored pitch decks without designer involvement. "
            "Academics and trainers generate structured course material from syllabi automatically."
        ),
        "hal_use_case": (
            "HAL programme managers and design teams can use Gamma to rapidly generate technical "
            "briefings for DRDO reviews, MoD presentations, and international airshow displays. "
            "It reduces slide preparation time from days to hours and ensures consistent branding "
            "across LCA Tejas, ALH, and HTT-40 programme communications."
        ),
        "sample_prompt": (
            "Create a 10-slide executive briefing on the HAL Light Combat Helicopter (LCH) "
            "programme status, including capability overview, delivery milestones, and export potential."
        ),
        "website": "https://gamma.app",
        "website_display": "gamma.app",
        "pricing_tier": "Freemium",
        "pricing_details": "400 AI credits free; Unlimited plan at $10/month.",
        "security_note": (
            "⚠ Do not upload classified, ITAR-controlled, or project-sensitive data to external "
            "AI platforms. Verify data handling policies before use. — HAL IT Security"
        ),
    },
    {
        "name": "Notion AI",
        "category": "AI Productivity & Notes",
        "overview": (
            "Notion AI is an integrated AI assistant built into the Notion workspace platform, "
            "enabling users to draft, summarise, translate, and analyse documents directly within "
            "their knowledge base. It connects to your existing Notion pages for context-aware "
            "answers and automations, making it a powerful tool for teams managing complex documentation."
        ),
        "key_features": [
            "AI writing, summarisation, and editing inline within Notion pages",
            "Q&A over your entire Notion workspace with cited page references",
            "Automated action items extraction from meeting notes",
        ],
        "how_it_works": (
            "Notion AI is embedded natively in the Notion editor. Users invoke it with a '/AI' "
            "command or by selecting text. It has access to the user's full Notion workspace (with "
            "permission), enabling it to retrieve context from linked documents and databases before "
            "generating responses. Outputs are inserted directly into the page for review."
        ),
        "practical_applications": (
            "Engineering teams use Notion AI to auto-summarise lengthy design review documents "
            "and extract open action items. HR departments generate onboarding documents and policy "
            "summaries on demand. Project managers query the AI to track cross-team dependencies "
            "stored across multiple Notion databases."
        ),
        "hal_use_case": (
            "HAL's Design & Development departments can use Notion AI to build a centralised "
            "engineering knowledge base — summarising test reports, maintenance manuals, and "
            "RFP responses — and query it in natural language. This can accelerate document "
            "retrieval for LCA, ALH, and HTT programmes, reducing engineering search time significantly."
        ),
        "sample_prompt": (
            "Summarise all action items from last week's LCA Mk2 avionics integration review "
            "meeting notes and generate a priority-ranked task list for the systems team."
        ),
        "website": "https://www.notion.so",
        "website_display": "notion.so",
        "pricing_tier": "Freemium",
        "pricing_details": "Notion AI add-on at $10/member/month; free trial available.",
        "security_note": (
            "⚠ Do not upload classified, ITAR-controlled, or project-sensitive data to external "
            "AI platforms. Verify data handling policies before use. — HAL IT Security"
        ),
    },
]

ISSUE_INFO = {
    "issue_number": 1,
    "week_label": "Week 47, 2025",
    "pub_date": "17 November 2025",
    "title": "HAL AI Tools Weekly",
}

OUTPUT_PATH = "generated_newsletters/SAMPLE_HAL_AI_Tools_Weekly.pdf"


async def main():
    print("Generating sample newsletter PDF …")
    Path("generated_newsletters").mkdir(parents=True, exist_ok=True)

    creator = PDFCreator()
    pdf_path = await creator.generate_pdf(
        tools_data=SAMPLE_TOOLS,
        issue_info=ISSUE_INFO,
        output_path=OUTPUT_PATH,
    )
    print(f"Sample PDF saved to: {pdf_path}")
    print(f"Debug HTML saved to: {OUTPUT_PATH.replace('.pdf', '.html')}")


if __name__ == "__main__":
    asyncio.run(main())
