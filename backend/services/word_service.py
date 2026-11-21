"""Word document (.docx) generation service for HAL AI Tools Weekly."""

import logging
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

logger = logging.getLogger(__name__)

# Enterprise Brand Colors
NAVY = RGBColor(10, 25, 47)         # #0a192f
SAFFRON = RGBColor(224, 90, 27)     # #e05a1b
CHARCOAL = RGBColor(30, 41, 59)     # #1e293b
MUTED_GRAY = RGBColor(100, 116, 139)# #64748b
WHITE = RGBColor(255, 255, 255)
LIGHT_BG = "F1F5F9"
BORDER_COLOR = "CBD5E1"


def _set_cell_background(cell, fill_hex: str):
    """Set the background color of a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)


def _set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Set padding inside a table cell (values in twips, 20 twips = 1 pt)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)


class WordCreator:
    """Generates an executive, styled Microsoft Word (.docx) newsletter document."""

    def generate_docx(self, tools: list[dict], issue_info: dict, output_path: str) -> str:
        """
        Generate .docx file from tools content and issue information.

        Args:
            tools: list of tool dictionaries
            issue_info: dict containing issue_number, week_label, pub_date, title, etc.
            output_path: file path to save the .docx
        """
        doc = Document()

        # Set page size to A4 with 0.75-inch margins
        for section in doc.sections:
            section.page_width = Inches(8.27)
            section.page_height = Inches(11.69)
            section.top_margin = Inches(0.7)
            section.bottom_margin = Inches(0.7)
            section.left_margin = Inches(0.75)
            section.right_margin = Inches(0.75)

        issue_num = issue_info.get("issue_number", 1)
        pub_date = issue_info.get("pub_date", "November 2026")
        week_label = issue_info.get("week_label", "")

        # -------------------------------------------------------------------
        # Header / Banner Table
        # -------------------------------------------------------------------
        header_table = doc.add_table(rows=1, cols=1)
        header_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        header_table.autofit = False
        header_table.columns[0].width = Inches(6.77)

        cell = header_table.cell(0, 0)
        _set_cell_background(cell, "0A192F")
        _set_cell_margins(cell, top=180, bottom=180, left=200, right=200)

        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r1 = p.add_run("HINDUSTAN AERONAUTICS LIMITED\n")
        r1.bold = True
        r1.font.size = Pt(15)
        r1.font.color.rgb = WHITE

        r2 = p.add_run("HAL AI TOOLS WEEKLY — INTERNAL INTELLIGENCE BRIEFING")
        r2.bold = True
        r2.font.size = Pt(11)
        r2.font.color.rgb = RGBColor(224, 90, 27)

        # Metadata ribbon
        meta_table = doc.add_table(rows=1, cols=3)
        meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        meta_table.autofit = False
        meta_table.columns[0].width = Inches(2.25)
        meta_table.columns[1].width = Inches(2.25)
        meta_table.columns[2].width = Inches(2.27)

        cols_data = [
            ("ISSUE DETAILS", f"Issue #{issue_num:02d} | {week_label}"),
            ("DATE OF RELEASE", pub_date),
            ("SECURITY STATUS", "UNCLASSIFIED WORKFLOWS ONLY"),
        ]

        for i, (title, val) in enumerate(cols_data):
            c = meta_table.cell(0, i)
            _set_cell_background(c, "F8FAFC")
            _set_cell_margins(c, top=80, bottom=80, left=100, right=100)
            cp = c.paragraphs[0]
            cr1 = cp.add_run(f"{title}\n")
            cr1.font.size = Pt(8)
            cr1.font.bold = True
            cr1.font.color.rgb = MUTED_GRAY
            cr2 = cp.add_run(val)
            cr2.font.size = Pt(9)
            cr2.font.bold = True
            cr2.font.color.rgb = CHARCOAL

        doc.add_paragraph()  # spacer

        # -------------------------------------------------------------------
        # Iterate over tools
        # -------------------------------------------------------------------
        for idx, tool in enumerate(tools):
            tool_name = tool.get("name", "Featured AI Tool")
            category = tool.get("category", "Workplace Productivity")
            tool_idx = tool.get("tool_number", idx + 1)

            # Tool Header Card
            tool_table = doc.add_table(rows=1, cols=1)
            tool_table.alignment = WD_TABLE_ALIGNMENT.CENTER
            tool_table.autofit = False
            tool_table.columns[0].width = Inches(6.77)

            tc = tool_table.cell(0, 0)
            _set_cell_background(tc, "0A192F")
            _set_cell_margins(tc, top=140, bottom=140, left=180, right=180)

            tp = tc.paragraphs[0]
            tr0 = tp.add_run(f"TOOL {tool_idx:02d} OF {len(tools):02d} | ")
            tr0.font.size = Pt(9)
            tr0.font.bold = True
            tr0.font.color.rgb = RGBColor(224, 90, 27)

            tr1 = tp.add_run(f"{tool_name.upper()}\n")
            tr1.bold = True
            tr1.font.size = Pt(16)
            tr1.font.color.rgb = WHITE

            tr2 = tp.add_run(f"DOMAIN: {category.upper()}  •  TIER: {tool.get('pricing_tier', 'Freemium').upper()}  •  WEBSITE: {tool.get('website', '')}")
            tr2.font.size = Pt(8.5)
            tr2.font.color.rgb = RGBColor(203, 213, 225)

            # 1-Sentence Executive Overview Callout
            overview_text = tool.get("overview", "")
            if overview_text:
                op = doc.add_paragraph()
                op.paragraph_format.space_before = Pt(8)
                op.paragraph_format.space_after = Pt(4)
                orun = op.add_run(f"Executive Summary: {overview_text}")
                orun.font.size = Pt(10)
                orun.italic = True
                orun.font.color.rgb = CHARCOAL

            # Everyday Analogy (if present in GN3-HAL)
            analogy = tool.get("everyday_analogy", "")
            if analogy:
                ap = doc.add_paragraph()
                ap.paragraph_format.space_before = Pt(2)
                ap.paragraph_format.space_after = Pt(6)
                ar_title = ap.add_run("Everyday Analogy: ")
                ar_title.bold = True
                ar_title.font.size = Pt(9.5)
                ar_title.font.color.rgb = SAFFRON
                ar_body = ap.add_run(analogy)
                ar_body.font.size = Pt(9.5)
                ar_body.italic = True

            # Before & After Comparison (if present in GN3-HAL)
            bna = tool.get("before_and_after", {})
            if isinstance(bna, dict) and (bna.get("pain_before") or bna.get("relief_after")):
                bp = doc.add_paragraph()
                bp.paragraph_format.space_before = Pt(2)
                bp.paragraph_format.space_after = Pt(6)
                bp_title = bp.add_run("Workplace Transformation: ")
                bp_title.bold = True
                bp_title.font.size = Pt(9.5)
                bp_title.font.color.rgb = NAVY
                if bna.get("pain_before"):
                    b_pain = bp.add_run(f"\n• Before AI (The Pain): {bna.get('pain_before')}")
                    b_pain.font.size = Pt(9)
                    b_pain.font.color.rgb = RGBColor(180, 40, 40)
                if bna.get("relief_after"):
                    b_relief = bp.add_run(f"\n• With Tool (The Relief): {bna.get('relief_after')}")
                    b_relief.font.size = Pt(9)
                    b_relief.font.color.rgb = RGBColor(20, 120, 60)

            # Section: Top Capabilities
            h2_caps = doc.add_heading(level=2)
            h2_caps_run = h2_caps.add_run("Top Capabilities & Core Features")
            h2_caps_run.font.size = Pt(12)
            h2_caps_run.font.color.rgb = NAVY

            key_features = tool.get("key_features", [])
            for feat in key_features:
                fp = doc.add_paragraph(style='List Bullet')
                fp.paragraph_format.space_after = Pt(3)
                if ":" in feat:
                    title, desc = feat.split(":", 1)
                    r_title = fp.add_run(title.strip() + ": ")
                    r_title.bold = True
                    r_title.font.size = Pt(9.5)
                    r_desc = fp.add_run(desc.strip())
                    r_desc.font.size = Pt(9.5)
                else:
                    r = fp.add_run(feat)
                    r.font.size = Pt(9.5)

            # Section: How It Works (3-Step Workflow)
            h2_how = doc.add_heading(level=2)
            h2_how_run = h2_how.add_run("How It Works — 3-Step Operating Cycle")
            h2_how_run.font.size = Pt(12)
            h2_how_run.font.color.rgb = NAVY

            how_steps = tool.get("how_it_works_steps", [])
            if how_steps and isinstance(how_steps, list):
                for step in how_steps:
                    sp = doc.add_paragraph()
                    sp.paragraph_format.space_after = Pt(3)
                    s_num = sp.add_run(f"Step {step.get('step', '')}: {step.get('title', '')} — ")
                    s_num.bold = True
                    s_num.font.size = Pt(9.5)
                    s_num.font.color.rgb = SAFFRON
                    s_desc = sp.add_run(step.get('description', ''))
                    s_desc.font.size = Pt(9.5)
            else:
                hp = doc.add_paragraph()
                hr = hp.add_run(tool.get("how_it_works", ""))
                hr.font.size = Pt(9.5)

            # Section: Workplace Application & Use Case
            h2_use = doc.add_heading(level=2)
            h2_use_run = h2_use.add_run("Workplace Application at HAL")
            h2_use_run.font.size = Pt(12)
            h2_use_run.font.color.rgb = NAVY

            use_p = doc.add_paragraph()
            use_p.paragraph_format.space_after = Pt(3)
            use_r = use_p.add_run(tool.get("hal_use_case", ""))
            use_r.font.size = Pt(9.5)

            ex_wf = tool.get("hal_example_workflow", "")
            if ex_wf:
                wf_p = doc.add_paragraph()
                wf_p.paragraph_format.space_after = Pt(4)
                wf_lbl = wf_p.add_run("Practical Example: ")
                wf_lbl.bold = True
                wf_lbl.font.size = Pt(9.5)
                wf_lbl.font.color.rgb = SAFFRON
                wf_val = wf_p.add_run(ex_wf)
                wf_val.font.size = Pt(9.5)

            # Adaptive Workflow / Prompt
            adaptive = tool.get("adaptive_workflow", {})
            action_p = doc.add_paragraph()
            action_p.paragraph_format.space_after = Pt(4)
            if adaptive and adaptive.get("mode_label"):
                act_lbl = action_p.add_run(f"Operating Trigger ({adaptive.get('mode_label')}): ")
                act_lbl.bold = True
                act_lbl.font.size = Pt(9.5)
                act_lbl.font.color.rgb = NAVY
                act_val = action_p.add_run(f"{adaptive.get('primary_action', '')} | {adaptive.get('guidance_tip', '')}")
                act_val.font.size = Pt(9.5)
            else:
                prompt = tool.get("sample_prompt", "")
                if prompt:
                    act_lbl = action_p.add_run("Sample Prompt: ")
                    act_lbl.bold = True
                    act_lbl.font.size = Pt(9.5)
                    act_lbl.font.color.rgb = NAVY
                    act_val = action_p.add_run(f'"{prompt}"')
                    act_val.font.size = Pt(9.5)

            # At-A-Glance Impact Table
            at_glance = tool.get("at_a_glance", {})
            if at_glance:
                imp_table = doc.add_table(rows=1, cols=4)
                imp_table.alignment = WD_TABLE_ALIGNMENT.CENTER
                imp_table.autofit = False
                imp_table.columns[0].width = Inches(1.7)
                imp_table.columns[1].width = Inches(1.7)
                imp_table.columns[2].width = Inches(1.7)
                imp_table.columns[3].width = Inches(1.67)

                items = [
                    ("TIME SAVINGS", at_glance.get("time_savings", "~3 to 5 hrs/week")),
                    ("EFFICIENCY", at_glance.get("efficiency_gain", "Up to 60% faster")),
                    ("TARGET TEAMS", at_glance.get("target_teams", "Engineering & Ops")),
                    ("LEARNING CURVE", at_glance.get("learning_curve", "Low (15 mins)")),
                ]
                for c_i, (k, v) in enumerate(items):
                    c = imp_table.cell(0, c_i)
                    _set_cell_background(c, "F1F5F9")
                    _set_cell_margins(c, top=60, bottom=60, left=80, right=80)
                    cp = c.paragraphs[0]
                    cr1 = cp.add_run(f"{k}\n")
                    cr1.font.size = Pt(7.5)
                    cr1.font.bold = True
                    cr1.font.color.rgb = MUTED_GRAY
                    cr2 = cp.add_run(v)
                    cr2.font.size = Pt(8.5)
                    cr2.font.bold = True
                    cr2.font.color.rgb = NAVY

            # ---------------------------------------------------------------
            # Part 2: Enterprise Deep-Dive Dossier (if present)
            # ---------------------------------------------------------------
            p2 = tool.get("page_2_dossier", {})
            if p2:
                doc.add_page_break()

                # Dossier Subheader
                p2_hdr = doc.add_table(rows=1, cols=1)
                p2_hdr.alignment = WD_TABLE_ALIGNMENT.CENTER
                p2_hdr.autofit = False
                p2_hdr.columns[0].width = Inches(6.77)
                p2_c = p2_hdr.cell(0, 0)
                _set_cell_background(p2_c, "0A192F")
                _set_cell_margins(p2_c, top=100, bottom=100, left=150, right=150)
                p2_hp = p2_c.paragraphs[0]
                p2_hr1 = p2_hp.add_run(f"{tool_name.upper()} — ENTERPRISE DOSSIER & DEEP DIVE\n")
                p2_hr1.font.size = Pt(13)
                p2_hr1.font.bold = True
                p2_hr1.font.color.rgb = WHITE
                p2_hr2 = p2_hp.add_run("Technical Architecture, Measurable Workplace Impact & Security Protocols")
                p2_hr2.font.size = Pt(9)
                p2_hr2.font.color.rgb = RGBColor(224, 90, 27)

                # 1. Enterprise Integration Architecture
                integ = p2.get("integration_architecture", {})
                h3_int = doc.add_heading(level=2)
                h3_int_run = h3_int.add_run("1. Enterprise Integration Architecture")
                h3_int_run.font.size = Pt(11)
                h3_int_run.font.color.rgb = NAVY

                int_bullets = [
                    f"Deployment Environment: {integ.get('environment', 'Browser-based SAS / Local client')}",
                    f"Computation & Privacy Model: {integ.get('computation_model', 'Cloud API / Local inference')}",
                    f"Supported File Formats: {integ.get('supported_formats', 'PDF, DOCX, CSV, TXT')}",
                    f"Configuration & Setup: {integ.get('setup_prerequisites', 'Standard SSO or corporate registration')}",
                ]
                for b in int_bullets:
                    bp = doc.add_paragraph(style='List Bullet')
                    bp.paragraph_format.space_after = Pt(2)
                    k_txt, v_txt = b.split(":", 1)
                    rk = bp.add_run(k_txt + ": ")
                    rk.bold = True
                    rk.font.size = Pt(9)
                    rv = bp.add_run(v_txt.strip())
                    rv.font.size = Pt(9)

                # 2. 3-Phase Pilot Rollout Roadmap
                h3_road = doc.add_heading(level=2)
                h3_road_run = h3_road.add_run("2. 3-Phase Pilot Rollout Roadmap")
                h3_road_run.font.size = Pt(11)
                h3_road_run.font.color.rgb = NAVY

                roadmap_steps = [
                    ("Phase 01: IT Compliance Audit & Local Sandbox", "Validate privacy boundaries and install plugin in isolated corporate test environment."),
                    ("Phase 02: Functional Pilot & Efficiency Benchmark", "Deploy to designated engineers to benchmark turnaround time on unclassified workflows."),
                    ("Phase 03: Departmental Standardization & SOP Release", "Publish approved templates and guidelines across divisions for scaled, safe adoption."),
                ]
                for r_title, r_desc in roadmap_steps:
                    rp = doc.add_paragraph(style='List Bullet')
                    rp.paragraph_format.space_after = Pt(2)
                    rt = rp.add_run(r_title + " — ")
                    rt.bold = True
                    rt.font.size = Pt(9)
                    rd = rp.add_run(r_desc)
                    rd.font.size = Pt(9)

                # 3. Real-World Case Study
                case = p2.get("case_study", {})
                h3_case = doc.add_heading(level=2)
                h3_case_run = h3_case.add_run(f"3. Workplace Case Study: {case.get('scenario_title', 'Operational Workflow')}")
                h3_case_run.font.size = Pt(11)
                h3_case_run.font.color.rgb = NAVY

                case_p = doc.add_paragraph()
                case_p.paragraph_format.space_after = Pt(2)
                c_lbl1 = case_p.add_run("Context & Challenge: ")
                c_lbl1.bold = True
                c_lbl1.font.size = Pt(9)
                c_val1 = case_p.add_run(case.get("context", "") + "\n")
                c_val1.font.size = Pt(9)

                c_lbl2 = case_p.add_run("Input Payload: ")
                c_lbl2.bold = True
                c_lbl2.font.size = Pt(9)
                c_val2 = case_p.add_run(case.get("raw_input_sample", "") + "\n")
                c_val2.font.size = Pt(9)

                c_lbl3 = case_p.add_run("Transformation & Outcome: ")
                c_lbl3.bold = True
                c_lbl3.font.size = Pt(9)
                c_val3 = case_p.add_run(case.get("transformation_step", "") + " → " + case.get("final_deliverable", ""))
                c_val3.font.size = Pt(9)

                # 4. Data Governance & Security Matrix
                gov = p2.get("governance_matrix", {})
                h3_gov = doc.add_heading(level=2)
                h3_gov_run = h3_gov.add_run("4. Enterprise Data Governance Matrix")
                h3_gov_run.font.size = Pt(11)
                h3_gov_run.font.color.rgb = NAVY

                gov_table = doc.add_table(rows=1, cols=2)
                gov_table.alignment = WD_TABLE_ALIGNMENT.CENTER
                gov_table.autofit = False
                gov_table.columns[0].width = Inches(3.38)
                gov_table.columns[1].width = Inches(3.39)

                gc1 = gov_table.cell(0, 0)
                _set_cell_background(gc1, "F0FDF4") # soft green
                _set_cell_margins(gc1, top=80, bottom=80, left=100, right=100)
                gp1 = gc1.paragraphs[0]
                gr1 = gp1.add_run("✓ PERMITTED DATA WORKFLOWS\n")
                gr1.font.size = Pt(9)
                gr1.bold = True
                gr1.font.color.rgb = RGBColor(22, 101, 52)
                for item in gov.get("permitted_data", []):
                    gitem = gp1.add_run(f"• {item}\n")
                    gitem.font.size = Pt(8.5)

                gc2 = gov_table.cell(0, 1)
                _set_cell_background(gc2, "FEF2F2") # soft red
                _set_cell_margins(gc2, top=80, bottom=80, left=100, right=100)
                gp2 = gc2.paragraphs[0]
                gr2 = gp2.add_run("✗ STRICTLY PROHIBITED DATA\n")
                gr2.font.size = Pt(9)
                gr2.bold = True
                gr2.font.color.rgb = RGBColor(153, 27, 27)
                for item in gov.get("prohibited_data", []):
                    gitem2 = gp2.add_run(f"• {item}\n")
                    gitem2.font.size = Pt(8.5)

                # 5. Mandatory Quality & Verification Gates
                h3_gate = doc.add_heading(level=2)
                h3_gate_run = h3_gate.add_run("5. Mandatory Quality & Verification Gates")
                h3_gate_run.font.size = Pt(11)
                h3_gate_run.font.color.rgb = NAVY

                hitl_gates = [
                    ("Gate 1: Source Grounding", "Confirm all generated logic or citations match original project documentation."),
                    ("Gate 2: Sanitization Audit", "Verify zero classified parameters, proprietary formulas, or ITAR data were exposed."),
                    ("Gate 3: Peer Review & Sign-off", "Obtain formal peer or lead review before committing deliverables to shared repos."),
                ]
                for g_title, g_desc in hitl_gates:
                    gp = doc.add_paragraph(style='List Bullet')
                    gp.paragraph_format.space_after = Pt(2)
                    gt = gp.add_run(g_title + " — ")
                    gt.bold = True
                    gt.font.size = Pt(9)
                    gd = gp.add_run(g_desc)
                    gd.font.size = Pt(9)

                # 6. Enterprise FAQ & IT Policies
                faqs = p2.get("enterprise_faq", [])
                if faqs:
                    h3_faq = doc.add_heading(level=2)
                    h3_faq_run = h3_faq.add_run("6. Enterprise FAQ & IT Policies")
                    h3_faq_run.font.size = Pt(11)
                    h3_faq_run.font.color.rgb = NAVY

                    for f in faqs:
                        fp = doc.add_paragraph()
                        fp.paragraph_format.space_after = Pt(2)
                        fq = fp.add_run(f"Q: {f.get('q', '')}\n")
                        fq.bold = True
                        fq.font.size = Pt(9)
                        fq.font.color.rgb = CHARCOAL
                        fa = fp.add_run(f"A: {f.get('a', '')}")
                        fa.font.size = Pt(8.5)

            # Add page break before next tool if not last
            if idx < len(tools) - 1:
                doc.add_page_break()

        # Save document
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        doc.save(output_path)
        logger.info("Successfully generated Word document: %s", output_path)
        return output_path
