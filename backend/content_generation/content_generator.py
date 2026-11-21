"""Orchestrates Gemini content generation and JSON validation."""

import json
import logging
import re

from backend.content_generation.gemini_client import GeminiClient
from backend.content_generation.prompt_templates import TOOL_CONTENT_PROMPT, GN3_HAL_CONTENT_PROMPT

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

    async def generate_tool_content(
        self,
        tool_data: dict,
        custom_focus: str | None = None,
        template_name: str = "classic",
    ) -> dict:
        """
        Generate structured content for a single AI tool.

        Args:
            tool_data: dict with at minimum {name, category, website, research_data}
            custom_focus: optional user focus/instruction to guide the angle of content
            template_name: "classic" | "modern" | "gn3_hal"

        Returns:
            Validated dict with all required content fields.
        """
        custom_focus_section = ""
        if custom_focus:
            custom_focus_section = f"\n## Editorial Direction / Custom Focus\nPlease tailor the content, practical examples, and workflow guidance towards this focus: {custom_focus}\n"

        selected_prompt_template = (
            GN3_HAL_CONTENT_PROMPT if template_name == "gn3_hal" else TOOL_CONTENT_PROMPT
        )

        prompt = selected_prompt_template.format(
            tool_name=tool_data.get("name", "Unknown Tool"),
            category=tool_data.get("category", "AI Tool"),
            website=tool_data.get("website", ""),
            research_data=tool_data.get("research_data", "No research data available."),
            custom_focus_section=custom_focus_section,
        )

        raw = await self.gemini.generate(prompt)
        content = self._parse_json(raw)
        content = self._validate_and_patch(content, tool_data, is_gn3_hal=(template_name == "gn3_hal"))
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

    def _validate_and_patch(self, content: dict, tool_data: dict, is_gn3_hal: bool = False) -> dict:
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
                    if is_gn3_hal:
                        content["overview"] = f"{tool_name} is a friendly workplace AI helper that takes the routine work out of daily {category.lower()} tasks, giving you more time to focus on what matters."
                    else:
                        content["overview"] = f"Think of {tool_name} as an intelligent digital assistant that streamlines {category.lower()} workflows, helping teams save hours of manual effort."
                elif field == "what_it_does":
                    if is_gn3_hal:
                        content["what_it_does"] = f"{tool_name} helps employees draft letters, organize messy lists, summarize lengthy booklets, and answer questions instantly in plain words."
                    else:
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

        # GN3-HAL specific fields: everyday_analogy & before_and_after
        if is_gn3_hal or "everyday_analogy" in content:
            if not content.get("everyday_analogy"):
                content["everyday_analogy"] = f"Think of {tool_name} like your smartphone's autocorrect, but for whole office memos, spreadsheets, and equipment checklists."

        if is_gn3_hal or "before_and_after" in content:
            bna = content.get("before_and_after")
            if not isinstance(bna, dict):
                bna = {}
            bna.setdefault("pain_before", "Spending 2 to 3 hours manually reading, copying, and reformatting notes between different documents and spreadsheets.")
            bna.setdefault("relief_after", f"With {tool_name}, ask what you need in plain words and receive a clean, finished draft in under 60 seconds.")
            content["before_and_after"] = bna

        # 2. Key features (ensure list of 5 items for full vertical fill)
        kf = content.get("key_features")
        if not isinstance(kf, list) or len(kf) < 5:
            existing = [str(f) for f in (kf or [])]
            fallback_features = [
                f"Easy Daily Automation: Handles repetitive {category.lower()} tasks so you don't have to type them manually.",
                "Instant Plain-English Answers: Understands normal everyday questions without needing technical commands.",
                "Ready-to-Use Formatting: Turns rough notes or vendor files into tidy, formatted tables and summaries.",
                "Zero Installation Hassle: Opens directly in your regular web browser with straightforward access.",
                "Human-in-the-Loop Review: Keeps you in complete control to review and adjust every output before sharing."
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
                    "title": "Provide Material" if is_gn3_hal else "Define & Connect",
                    "desc": f"Drop in your messy notes, open your spreadsheet, or paste standard text directly into {tool_name}."
                },
                {
                    "step": "02",
                    "title": "Ask in Plain Words" if is_gn3_hal else "Intelligent Processing",
                    "desc": "Type what you need in normal everyday English—just like asking a colleague at the next desk."
                },
                {
                    "step": "03",
                    "title": "Review & Use Output" if is_gn3_hal else "Review & Apply",
                    "desc": "Check the organized summary or table, make any quick adjustments, and put it to work immediately."
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
                    "icon": "📋",
                    "title": "Office & Administration",
                    "desc": "Draft clean memos, summarize meeting notes, and prepare announcements in minutes."
                },
                {
                    "icon": "📦",
                    "title": "Stores & Procurement",
                    "desc": "Compare vendor quotes, organize item descriptions, and track incoming delivery lists."
                },
                {
                    "icon": "🔧",
                    "title": "Maintenance & Inspection",
                    "desc": "Convert lengthy tool manuals into clear, step-by-step daily equipment checklists."
                }
            ]
        else:
            patched_wih = []
            default_icons = ["📋", "📦", "🔧"] if is_gn3_hal else ["📝", "📊", "⚙️"]
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
        fs.setdefault("input_badge", "STEP 1: INPUT" if is_gn3_hal else "INPUT")
        fs.setdefault("input_icon", "📄")
        fs.setdefault("input_title", "Messy Notes or Data" if is_gn3_hal else "Source Files / Data")
        fs.setdefault("input_desc", "Rough notes or standard documents")
        fs.setdefault("ai_step_badge", "STEP 2: SIMPLE AI" if is_gn3_hal else "AI STEP")
        fs.setdefault("ai_step_icon", "✨" if is_gn3_hal else "⚡")
        fs.setdefault("ai_step_title", "Plain English Request" if is_gn3_hal else "Contextual Processing")
        fs.setdefault("ai_step_desc", "Ask in everyday language")
        fs.setdefault("output_badge", "STEP 3: READY OUTPUT" if is_gn3_hal else "OUTPUT")
        fs.setdefault("output_icon", "✅" if is_gn3_hal else "📊")
        fs.setdefault("output_title", "Tidy Deliverable" if is_gn3_hal else "Verified Deliverable")
        fs.setdefault("output_desc", "Clean summary, list, or table")
        fs.setdefault("key_advantage", f"Eliminates hours of tedious manual typing and repetitive paperwork.")
        content["feature_snapshot"] = fs

        # 6. Impact Metrics (Fills Column 3 below Feature Snapshot)
        im = content.get("impact_metrics")
        if not isinstance(im, dict):
            im = {}
        im.setdefault("time_saved", "~3 to 5 hours saved every week on routine office paperwork")
        im.setdefault("key_metric", "Finish routine drafts 70% faster")
        im.setdefault("target_departments", "Administration, Stores, Maintenance, Accounts, Quality")
        im.setdefault("learning_curve", "Zero (No technical skills needed, works like a standard search)")
        content["impact_metrics"] = im

        # 7. Adaptive Workflow (Dual Prompts or Shortcuts/Triggers - NO "N/A"!)
        aw = content.get("adaptive_workflow")
        if not isinstance(aw, dict):
            sp = content.get("sample_prompt")
            ap = content.get("advanced_prompt")
            aw = {
                "label": "60-SECOND QUICK TRYOUT (COPY & PASTE TODAY)" if is_gn3_hal else "TRY IT IN YOUR WORKFLOW",
                "standard_title": "EVERYDAY 60-SECOND TRYOUT PROMPT" if is_gn3_hal else "ROUTINE TASK PROMPT",
                "standard_body": sp or f"Please summarize this equipment overview into 3 simple bullet points for our daily shift handover meeting.",
                "advanced_title": "ORGANIZED COMPARISON SHORTCUT" if is_gn3_hal else "ADVANCED POWER WORKFLOW",
                "advanced_body": ap or f"Compare the two lists below, highlight any items with different quantities or descriptions, and put the result in a neat 3-column table."
            }
        else:
            aw.setdefault("label", "60-SECOND QUICK TRYOUT" if is_gn3_hal else "TRY IT IN YOUR WORKFLOW")
            aw.setdefault("standard_title", "EVERYDAY TRYOUT PROMPT" if is_gn3_hal else "STANDARD WORKFLOW")
            aw.setdefault("standard_body", f"Please organize these meeting notes into a 3-point action checklist with assigned names.")
            aw.setdefault("advanced_title", "TABLE ORGANIZER SHORTCUT" if is_gn3_hal else "ADVANCED CONFIGURATION")
            aw.setdefault("advanced_body", f"Convert the following unstructured list into a clear table with columns for Item, Quantity, and Status.")
        content["adaptive_workflow"] = aw

        # 8. Page 2 Dossier (Zero Redundancy, Zero Empty Space)
        p2 = content.get("page_2_dossier")
        if not isinstance(p2, dict):
            p2 = {}
        
        # Integration Architecture / Quickstart
        ia = p2.get("integration_architecture") if isinstance(p2.get("integration_architecture"), dict) else {}
        ia.setdefault("environment", "Standard web browsers (Chrome, Edge), Excel/Office, or Desktop.")
        ia.setdefault("computation_model", "Runs securely in browser without needing special technical hardware.")
        ia.setdefault("file_formats", ".docx (Word), .xlsx (Excel), .pdf, .txt")
        ia.setdefault("setup_instructions", f"Visit {content.get('website_display', 'the approved portal')}, log in with your standard corporate account, and paste your non-sensitive text to begin.")
        p2["integration_architecture"] = ia

        # Case Study
        cs = p2.get("case_study") if isinstance(p2.get("case_study"), dict) else {}
        cs.setdefault("title", "Organizing 30 Vendor Quotation Notes in 4 Minutes")
        cs.setdefault("context", "A store supervisor received 30 different quotation emails with mismatched details, facing 4 hours of tedious manual data entry.")
        cs.setdefault("input_sample", "30 unclassified supplier email excerpts containing parts, quantities, and lead times.")
        cs.setdefault("ai_transformation", f"{tool_name} read the excerpts, extracted part numbers and prices, and organized everything into a unified comparison list.")
        cs.setdefault("final_deliverable", "A clean single-page comparison table ready for the manager's review, completed in under 4 minutes.")
        p2["case_study"] = cs

        # Governance Matrix (Permitted vs Prohibited)
        gm = p2.get("governance_matrix") if isinstance(p2.get("governance_matrix"), dict) else {}
        gm.setdefault("permitted_data", [
            "Public equipment manuals, catalog brochures, and commercial standards",
            "General office meeting agendas, scheduling notes, and training material",
            "Unclassified routine spreadsheets, inventory forms, and administrative memos"
        ])
        gm.setdefault("prohibited_data", [
            "Classified defense project files, aircraft telemetry, or flight control code",
            "Confidential commercial contracts, private employee salaries, or passwords",
            "Restricted engineering drawings, proprietary CAD files, or ITAR data"
        ])
        p2["governance_matrix"] = gm

        # Enterprise FAQ
        faq = p2.get("enterprise_faq")
        if not isinstance(faq, list) or len(faq) < 3:
            p2["enterprise_faq"] = [
                {
                    "q": "Do I need any programming or computer science skills to use this?",
                    "a": "Not at all! If you know how to search on Google or type an email, you can use this tool immediately."
                },
                {
                    "q": "Will this tool replace my job at HAL?",
                    "a": "No. AI acts like a digital calculator for words and paperwork. You remain the expert who reviews and approves all final deliverables."
                },
                {
                    "q": "Is it safe to type workplace information into this tool?",
                    "a": "Yes for general unclassified work, but NEVER upload classified, military defense, or confidential company secrets. Check the safety shield."
                }
            ]
        content["page_2_dossier"] = p2

        return content
