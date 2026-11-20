"""Orchestrates Gemini content generation and JSON validation."""

import json
import logging
import re

from backend.content_generation.gemini_client import GeminiClient
from backend.content_generation.prompt_templates import TOOL_CONTENT_PROMPT

logger = logging.getLogger(__name__)

REQUIRED_FIELDS = [
    "name", "category", "overview", "what_it_does", "key_features", "how_it_works",
    "how_it_works_steps", "where_it_helps", "feature_snapshot", "impact_metrics",
    "practical_applications", "hal_use_case", "hal_example_workflow",
    "adaptive_workflow", "page_2_dossier",
    "website", "website_display", "pricing_tier", "pricing_details", "security_note",
]


class ContentGenerator:
    """Uses GeminiClient to generate and validate newsletter content for one tool."""

    def __init__(self):
        self.gemini = GeminiClient()

    async def generate_tool_content(self, tool_data: dict, custom_focus: str | None = None) -> dict:
        """
        Generate structured content for a single AI tool.

        Args:
            tool_data: dict with at minimum {name, category, website, research_data}
            custom_focus: optional user focus/instruction to guide the angle of content

        Returns:
            Validated dict with all required content fields.
        """
        custom_focus_section = ""
        if custom_focus:
            custom_focus_section = f"\n## Editorial Direction / Custom Focus\nPlease tailor the content, practical examples, and workflow guidance towards this focus: {custom_focus}\n"

        prompt = TOOL_CONTENT_PROMPT.format(
            tool_name=tool_data.get("name", "Unknown Tool"),
            category=tool_data.get("category", "AI Tool"),
            website=tool_data.get("website", ""),
            research_data=tool_data.get("research_data", "No research data available."),
            custom_focus_section=custom_focus_section,
        )

        raw = await self.gemini.generate(prompt)
        content = self._parse_json(raw)
        content = self._validate_and_patch(content, tool_data)
        return content

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _parse_json(self, raw: str) -> dict:
        """Extract JSON from Gemini response (strips markdown fences if present)."""
        cleaned = re.sub(r"^```(?:json)?\s*", "", raw.strip(), flags=re.MULTILINE)
        cleaned = re.sub(r"```\s*$", "", cleaned.strip(), flags=re.MULTILINE).strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                return json.loads(match.group())
            logger.error("Could not parse JSON from Gemini response:\n%s", raw[:500])
            raise ValueError("Gemini did not return valid JSON.")

    def _validate_and_patch(self, content: dict, tool_data: dict) -> dict:
        """Ensure all required fields are present; fill defaults from tool_data."""
        tool_name = content.get("name") or tool_data.get("name", "AI Tool")
        category = content.get("category") or tool_data.get("category", "Workplace Productivity")

        # 1. Basic text fields (Safe, non-classified, plain-English defaults)
        for field in ["name", "category", "overview", "what_it_does", "how_it_works",
                      "practical_applications", "hal_use_case", "hal_example_workflow",
                      "website", "website_display", "pricing_tier", "pricing_details", "security_note"]:
            if not content.get(field):
                if field == "name":
                    content["name"] = tool_name
                elif field == "category":
                    content["category"] = category
                elif field == "overview":
                    content["overview"] = f"Think of {tool_name} as an intelligent digital assistant that streamlines {category.lower()} workflows, helping teams save hours of manual effort."
                elif field == "what_it_does":
                    content["what_it_does"] = f"{tool_name} simplifies complex engineering and administrative workflows by analyzing input data, automating repetitive tasks, and providing clean, verified outputs for immediate team collaboration."
                elif field == "how_it_works":
                    content["how_it_works"] = f"Users provide source data or open active project files; the AI processes the context in real-time, delivering structured deliverables under employee supervision."
                elif field == "practical_applications":
                    content["practical_applications"] = f"Practical applications include drafting documentation, organizing procurement tables, standardizing inspection reports, and preparing review presentations."
                elif field == "hal_use_case":
                    content["hal_use_case"] = f"Employees across engineering, operations, and administrative divisions can leverage {tool_name} to standardize equipment logs, summarize supplier guidelines, and compile monthly review packets."
                elif field == "hal_example_workflow":
                    content["hal_example_workflow"] = f"Standardizing equipment vendor guidelines into a concise 2-page operational checklist."
                elif field == "website":
                    content["website"] = tool_data.get("website", "")
                elif field == "website_display":
                    w = content.get("website") or tool_data.get("website", "")
                    content["website_display"] = w.replace("https://", "").replace("http://", "").rstrip("/")
                elif field == "pricing_tier":
                    content["pricing_tier"] = tool_data.get("pricing_tier", "Freemium")
                elif field == "pricing_details":
                    content["pricing_details"] = tool_data.get("pricing_details", "Free basic tier available; premium plans for advanced features.")
                elif field == "security_note":
                    content["security_note"] = "⚠ Do not upload classified, proprietary, or project-sensitive company data to external AI platforms. — HAL IT Security"

        # 2. Key features (ensure list of 5 items for full vertical fill)
        kf = content.get("key_features")
        if not isinstance(kf, list) or len(kf) < 5:
            existing = [str(f) for f in (kf or [])]
            fallback_features = [
                f"Intelligent Automation: Automates routine {category.lower()} operations based on real-time task context.",
                f"Context-Aware Processing: Analyzes surrounding information to generate highly relevant, structured suggestions.",
                f"Standardized Formatting: Converts raw, unstructured notes into publication-ready documents and tables.",
                f"Rapid Team Export: Easily transfers completed outputs into common enterprise office and code tools.",
                f"Error Reduction: Identifies discrepancies early to maintain high accuracy across team deliverables."
            ]
            while len(existing) < 5:
                existing.append(fallback_features[len(existing)])
            content["key_features"] = existing[:5]
        else:
            content["key_features"] = [str(f) for f in kf[:5]]

        # 3. How it works steps (ensure 3 distinct chronological steps)
        steps = content.get("how_it_works_steps")
        if not isinstance(steps, list) or len(steps) < 3:
            content["how_it_works_steps"] = [
                {
                    "step": "01",
                    "title": "Define & Connect",
                    "desc": f"Open your project workspace or provide non-sensitive source files directly to {tool_name}."
                },
                {
                    "step": "02",
                    "title": "Intelligent Processing",
                    "desc": "The engine parses structure, extracts key relationships, and synthesizes outputs in real-time."
                },
                {
                    "step": "03",
                    "title": "Review & Apply",
                    "desc": "Verify the suggestions, adjust parameters as needed, and export for immediate team distribution."
                }
            ]
        else:
            patched_steps = []
            for i, s in enumerate(steps[:3]):
                num = f"0{i+1}"
                title = s.get("title") if isinstance(s, dict) and s.get("title") else f"Step {num}"
                desc = s.get("desc") if isinstance(s, dict) and s.get("desc") else "Complete task workflow."
                patched_steps.append({"step": num, "title": title, "desc": desc})
            content["how_it_works_steps"] = patched_steps

        # 4. Where it helps (ensure 3 cards)
        wih = content.get("where_it_helps")
        if not isinstance(wih, list) or len(wih) < 3:
            content["where_it_helps"] = [
                {
                    "icon": "📝",
                    "title": "Standard Operating Procedures",
                    "desc": "Standardize team guidelines, draft review summaries, and create clear manuals."
                },
                {
                    "icon": "📊",
                    "title": "Procurement & Vendor Data",
                    "desc": "Compare vendor quotes, track expenditure logs, and surface cost efficiencies."
                },
                {
                    "icon": "⚙️",
                    "title": "Quality Assurance Reports",
                    "desc": "Aggregate test records and maintenance checklists into clean management briefs."
                }
            ]
        else:
            patched_wih = []
            default_icons = ["📝", "📊", "⚙️"]
            for i, item in enumerate(wih[:3]):
                if isinstance(item, dict):
                    icon = item.get("icon") or default_icons[i]
                    title = item.get("title") or f"Domain {i+1}"
                    desc = item.get("desc") or "Streamlines daily workplace workflows."
                    patched_wih.append({"icon": icon, "title": title, "desc": desc})
                else:
                    patched_wih.append({"icon": default_icons[i], "title": f"Domain {i+1}", "desc": str(item)})
            content["where_it_helps"] = patched_wih

        # 5. Feature snapshot (Compact, ends cleanly after Key Advantage)
        fs = content.get("feature_snapshot")
        if not isinstance(fs, dict):
            fs = {}
        fs.setdefault("input_badge", "INPUT")
        fs.setdefault("input_icon", "📄")
        fs.setdefault("input_title", "Source Files / Data")
        fs.setdefault("input_desc", "Project files or requirements")
        fs.setdefault("ai_step_badge", "AI STEP")
        fs.setdefault("ai_step_icon", "⚡")
        fs.setdefault("ai_step_title", "Contextual Processing")
        fs.setdefault("ai_step_desc", "Automated synthesis & parsing")
        fs.setdefault("output_badge", "OUTPUT")
        fs.setdefault("output_icon", "📊")
        fs.setdefault("output_title", "Verified Deliverable")
        fs.setdefault("output_desc", "Structured, ready-to-use output")
        fs.setdefault("key_advantage", f"Eliminates hours of manual typing and repetitive documentation lookup.")
        content["feature_snapshot"] = fs

        # 6. Impact Metrics (Fills Column 3 below Feature Snapshot)
        im = content.get("impact_metrics")
        if not isinstance(im, dict):
            im = {}
        im.setdefault("time_saved", "~4 to 6 hrs/week on routine development or data tasks")
        im.setdefault("key_metric", "Up to 80% faster draft turnaround")
        im.setdefault("target_departments", "Engineering, Documentation, QA, Operations")
        im.setdefault("learning_curve", "Low (Immediate integration with standard tools)")
        content["impact_metrics"] = im

        # 7. Adaptive Workflow (Dual Prompts or Shortcuts/Triggers - NO "N/A"!)
        aw = content.get("adaptive_workflow")
        if not isinstance(aw, dict):
            # Check old sample_prompt fields if present
            sp = content.get("sample_prompt")
            ap = content.get("advanced_prompt")
            aw = {
                "label": "TRY IT IN YOUR WORKFLOW",
                "standard_title": "ROUTINE TASK PROMPT",
                "standard_body": sp or f"Review this technical summary and format the top 3 action items into a clean checklist.",
                "advanced_title": "ADVANCED POWER WORKFLOW",
                "advanced_body": ap or f"Analyze the variance between columns B and C in this dataset, highlight records deviating by >15%, and summarize probable causes."
            }
        else:
            aw.setdefault("label", "TRY IT IN YOUR WORKFLOW")
            aw.setdefault("standard_title", "STANDARD WORKFLOW")
            aw.setdefault("standard_body", f"Execute task: Standardize input data and generate structured report.")
            aw.setdefault("advanced_title", "ADVANCED CONFIGURATION")
            aw.setdefault("advanced_body", f"Fine-tune parameters to automate multi-file processing across project workspaces.")
        content["adaptive_workflow"] = aw

        # 8. Page 2 Dossier (Zero Redundancy, Zero Empty Space)
        p2 = content.get("page_2_dossier")
        if not isinstance(p2, dict):
            p2 = {}
        
        # Integration Architecture
        ia = p2.get("integration_architecture") if isinstance(p2.get("integration_architecture"), dict) else {}
        ia.setdefault("environment", "Standard web browsers (Chrome, Edge), Excel/Office add-in, or IDE extension.")
        ia.setdefault("computation_model", "Local on-device processing where supported; secure encrypted HTTPS enterprise transmission.")
        ia.setdefault("file_formats", ".pdf, .docx, .xlsx, .csv, .txt, .py, .json")
        ia.setdefault("setup_instructions", f"Access {tool_name} via approved enterprise portal. Verify extension permissions and configure local workspace paths before importing non-sensitive project files.")
        p2["integration_architecture"] = ia

        # Case Study
        cs = p2.get("case_study") if isinstance(p2.get("case_study"), dict) else {}
        cs.setdefault("title", "Standardizing Vendor Equipment Review Records")
        cs.setdefault("context", "A team received 45 pages of vendor equipment documentation with varying formatting, making technical compliance comparison slow and error-prone.")
        cs.setdefault("input_sample", "45-page unclassified equipment specification manual and a standardized 5-point inspection parameter template.")
        cs.setdefault("ai_transformation", f"{tool_name} ingested the source document, mapped vendor parameters against the 5 inspection points, and flagged 2 discrepancies.")
        cs.setdefault("final_deliverable", "A clean 2-page comparison table ready for quality lead sign-off, completed in under 4 minutes.")
        p2["case_study"] = cs

        # Governance Matrix (Permitted vs Prohibited)
        gm = p2.get("governance_matrix") if isinstance(p2.get("governance_matrix"), dict) else {}
        gm.setdefault("permitted_data", [
            "Public equipment manuals, standards, and vendor catalog datasheets",
            "Generic meeting agendas, internal scheduling notes, and non-sensitive minutes",
            "Unclassified administrative spreadsheets and routine utility scripts"
        ])
        gm.setdefault("prohibited_data", [
            "Classified defense program parameters, aircraft telemetry, or flight control code",
            "Proprietary CAD drawings, secret manufacturing formulas, or ITAR data",
            "Internal credentials, network topology, or confidential customer identifiers"
        ])
        p2["governance_matrix"] = gm

        # Enterprise FAQ
        faq = p2.get("enterprise_faq")
        if not isinstance(faq, list) or len(faq) < 3:
            p2["enterprise_faq"] = [
                {
                    "q": "Does this tool retain or train on uploaded company data?",
                    "a": "Under standard enterprise guidelines, queries and uploaded files must not be used to train public foundational models. Always verify team privacy settings."
                },
                {
                    "q": "Can employees use this tool offline or on closed internal networks?",
                    "a": "Tools with local compute options run directly on workstations; web portals require a secure internet connection and must only receive unclassified data."
                },
                {
                    "q": "What is the mandatory verification protocol before sharing outputs?",
                    "a": "All AI-generated summaries and calculations must be reviewed and validated by a qualified employee prior to formal release."
                }
            ]
        content["page_2_dossier"] = p2

        return content
