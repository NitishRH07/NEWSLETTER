"""Tool discovery and deep research using Gemini AI & Web Search."""

import asyncio
import json
import logging
import re
from typing import Any

from backend.research.web_search import WebSearcher
from backend.config.settings import settings
from backend.content_generation.gemini_client import GeminiClient

logger = logging.getLogger(__name__)

# Curated catalog of high-value AI tools for HAL engineers and corporate employees
CURATED_AI_TOOLS = [
    {
        "name": "Consensus",
        "category": "AI Research & Scientific Papers",
        "website": "https://consensus.app",
        "description": "AI search engine that searches through 200M+ peer-reviewed scientific research papers and extracts evidence-based consensus answers.",
        "pricing_tier": "Freemium",
        "pricing_details": "Free tier available; Premium at $8.99/month for unlimited searches.",
    },
    {
        "name": "Cursor",
        "category": "AI Code Editor & Automation",
        "website": "https://cursor.com",
        "description": "An AI-first code editor built for pair programming, repository-wide indexing, refactoring, and automated code generation.",
        "pricing_tier": "Freemium",
        "pricing_details": "Free tier available; Pro at $20/month with unlimited Claude 3.5 Sonnet queries.",
    },
    {
        "name": "Julius AI",
        "category": "AI Data Analysis & Graphing",
        "website": "https://julius.ai",
        "description": "AI data analyst that analyzes complex Excel spreadsheets, CSVs, and databases, generating interactive charts and statistical models.",
        "pricing_tier": "Freemium",
        "pricing_details": "Free basic tier; Pro at $17.99/month for unlimited data computations.",
    },
    {
        "name": "DeepL Write",
        "category": "AI Technical Writing & Translation",
        "website": "https://deepl.com/write",
        "description": "Advanced AI writing companion and neural machine translator for creating precise, professional technical documentation.",
        "pricing_tier": "Freemium",
        "pricing_details": "Free web version; Pro plans starting at $8.74/month for unlimited technical translation.",
    },
    {
        "name": "Phind",
        "category": "AI Search Engine for Developers",
        "website": "https://phind.com",
        "description": "Intelligent search engine optimized for software developers, engineers, and technical researchers with code references.",
        "pricing_tier": "Freemium",
        "pricing_details": "Free daily queries; Pro plan available at $20/month.",
    },
    {
        "name": "Elicit",
        "category": "AI Literature Review & Research",
        "website": "https://elicit.com",
        "description": "AI research assistant that automates literature reviews, synthesizes findings across papers, and extracts structured data from PDFs.",
        "pricing_tier": "Freemium",
        "pricing_details": "Free credits included; Plus plan at $10/month.",
    },
    {
        "name": "Claude Code",
        "category": "AI Terminal Automation & Engineering",
        "website": "https://claude.ai",
        "description": "Autonomous command-line AI assistant that edits files, executes builds, debugs unit test suites, and manages complex git workflows.",
        "pricing_tier": "Paid",
        "pricing_details": "Usage-based API pricing or Claude Pro subscription at $20/month.",
    },
    {
        "name": "Wolfram Alpha AI",
        "category": "Computational Intelligence & Engineering Math",
        "website": "https://wolframalpha.com",
        "description": "Computational knowledge engine providing symbolic mathematical solutions, engineering formulas, and scientific calculations.",
        "pricing_tier": "Freemium",
        "pricing_details": "Free basic computation; Pro at $7/month for step-by-step solutions.",
    },
    {
        "name": "Perplexity AI",
        "category": "AI Search & Research Engine",
        "website": "https://perplexity.ai",
        "description": "Conversational AI search engine delivering sourced, real-time answers with verified citations across technical standards and industry news.",
        "pricing_tier": "Freemium",
        "pricing_details": "Free tier available; Pro at $20/month with unlimited Deep Research.",
    },
    {
        "name": "Gamma.app",
        "category": "AI Presentation Generator",
        "website": "https://gamma.app",
        "description": "AI-powered presentation creator that generates polished executive briefings, technical slides, and visual decks from text outlines in seconds.",
        "pricing_tier": "Freemium",
        "pricing_details": "400 free AI credits on signup; Plus plan at $10/month.",
    },
    {
        "name": "Notion AI",
        "category": "AI Productivity & Knowledge Management",
        "website": "https://notion.so",
        "description": "Contextual AI writing assistant integrated into connected workspaces for summarizing technical notes, action items, and specifications.",
        "pricing_tier": "Paid",
        "pricing_details": "Add-on at $10/member/month; free trial included.",
    },
    {
        "name": "Otter.ai",
        "category": "AI Meeting Transcription & Notes",
        "website": "https://otter.ai",
        "description": "Automated meeting assistant that records audio, writes real-time notes, captures slides, and generates actionable summary checklists.",
        "pricing_tier": "Freemium",
        "pricing_details": "Free plan includes 300 monthly transcription minutes; Pro at $10/month.",
    },
    {
        "name": "ChatPDF",
        "category": "AI Document Q&A & Summarization",
        "website": "https://chatpdf.com",
        "description": "Fast AI document reader that lets users upload large technical manuals or research PDFs and chat directly with them in plain English.",
        "pricing_tier": "Freemium",
        "pricing_details": "Free tier handles up to 2 PDFs per day (120 pages each); Plus at $5/month.",
    },
]


class ToolResearcher:
    """Discovers new AI tools and gathers research data for each one."""

    def __init__(self):
        self.searcher = WebSearcher(
            engine=settings.search_engine,
            serpapi_key=settings.search_api_key,
        )
        self.gemini = GeminiClient()

    async def discover_tools(
        self,
        count: int = 3,
        exclude_names: list[str] | None = None,
        custom_prompt: str | None = None,
    ) -> list[dict]:
        """
        Return `count` unique AI tool dicts: {name, website, category, description}.
        Prioritizes dynamic AI discovery via Gemini; falls back to curated catalog.
        Supports custom_prompt to target specific tool niches or user-specified tools.
        """
        exclude_lower = {n.lower() for n in (exclude_names or [])}
        discovered: list[dict] = []

        # 1. Dynamic AI discovery via Gemini
        try:
            custom_instruction = ""
            if custom_prompt and custom_prompt.strip():
                custom_instruction = (
                    f"\nUSER CUSTOM INSTRUCTION / FOCUS:\n"
                    f"The editor wants tools specifically focused on: \"{custom_prompt.strip()}\".\n"
                    f"If the user specified exact tool names in their instruction, prioritize researching those exact tools!\n"
                    f"Otherwise, select tools that best match this specified theme or department need.\n"
                )

            prompt = (
                f"You are researching currently available AI tools for a weekly corporate newsletter "
                f"at Hindustan Aeronautics Limited (HAL). Recommend {count + 2} practical, currently active AI tools "
                f"useful for engineers, corporate managers, documenters, or technical employees.\n"
                f"{custom_instruction}\n"
                f"Do NOT include these previously published tools: {', '.join(exclude_names or ['none'])}\n\n"
                f"Return ONLY a valid JSON array with objects containing:\n"
                f"- name: official tool name\n"
                f"- website: official website URL (e.g. https://...)\n"
                f"- category: primary category (e.g. AI Coding, AI Research, AI Data Analysis, AI Documentation)\n"
                f"- description: 2 sentence plain English description of main features and everyday workplace value\n"
                f"- pricing_tier: Free | Freemium | Paid | Enterprise\n"
                f"- pricing_details: 1 concise sentence pricing info\n"
            )
            raw = await self.gemini.generate(prompt)
            cleaned = re.sub(r"```(?:json)?\s*", "", raw).strip().rstrip("`").strip()
            match = re.search(r"\[.*\]", cleaned, re.DOTALL)
            if match:
                items = json.loads(match.group())
                for item in items:
                    if len(discovered) >= count:
                        break
                    if item.get("name") and item["name"].lower() not in exclude_lower:
                        discovered.append(item)
                        exclude_lower.add(item["name"].lower())
                logger.info("Discovered %d tools via Gemini dynamic research.", len(discovered))
        except Exception as exc:
            logger.warning("Gemini dynamic tool discovery failed: %s — falling back to catalog", exc)

        # 2. Fill remaining slots from curated catalog if needed
        if len(discovered) < count:
            # If custom prompt was given, prioritize catalog items matching keywords
            if custom_prompt:
                keywords = [w.lower() for w in re.findall(r"\w+", custom_prompt) if len(w) > 3]
                for tool in CURATED_AI_TOOLS:
                    if len(discovered) >= count:
                        break
                    if tool["name"].lower() not in exclude_lower:
                        text = (tool["name"] + " " + tool["category"] + " " + tool["description"]).lower()
                        if any(kw in text for kw in keywords):
                            discovered.append(tool.copy())
                            exclude_lower.add(tool["name"].lower())

            # Regular unexcluded fill
            for tool in CURATED_AI_TOOLS:
                if len(discovered) >= count:
                    break
                if tool["name"].lower() not in exclude_lower:
                    discovered.append(tool.copy())
                    exclude_lower.add(tool["name"].lower())

        return discovered[:count]

    async def research_tool(self, tool_name: str, website: str) -> dict:
        """Gather research data for a specific tool."""
        snippets: list[str] = []
        try:
            results = await self.searcher.search(f"{tool_name} features review", num_results=3)
            for r in results:
                s = r.get("snippet", "").strip()
                if s:
                    snippets.append(s)
        except Exception:
            pass

        research_data = "\n\n".join(snippets) if snippets else f"{tool_name} is an advanced AI tool accessible at {website}."

        return {
            "name": tool_name,
            "website": website,
            "research_data": research_data,
        }
