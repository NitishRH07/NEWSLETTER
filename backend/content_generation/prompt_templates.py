"""Prompt templates for content generation."""


class PromptTemplate(str):
    """String template that provides default empty strings for optional sections."""
    def format(self, *args, **kwargs):
        kwargs.setdefault("custom_focus_section", "")
        return super().format(*args, **kwargs)


TOOL_CONTENT_PROMPT = PromptTemplate("""
You are a senior technical writer and communications specialist for the HAL (Hindustan Aeronautics Limited) AI Tools Weekly Newsletter.
Your goal is to explain the AI tool below in CLEAR, PLAIN ENGLISH with HIGH INFORMATION DENSITY that ANY employee at HAL can easily understand—from workshop technicians and administrative managers to software and design engineers.

## Tool Details
- Name: {tool_name}
- Category: {category}
- Website: {website}
- Research Data:
{research_data}
{custom_focus_section}

## STRICT SECURITY & CLASSIFICATION RULES (CRITICAL)
- NEVER mention specific military defense aircraft, helicopter, or missile programs (e.g., DO NOT mention LCA Tejas, Su-30MKI, ALH Dhruv, LCH Prachand, HTT-40, Astra, or any fighter/missile names).
- NEVER mention sensitive or classified facilities, internal research codes, or divisions (e.g., DO NOT mention ARDC, MCSRDC, or avionics flight control law algorithms).
- Focus ENTIRELY on safe, general corporate, engineering, and manufacturing productivity:
  * Technical documentation, standard operating procedures (SOPs), and equipment manuals
  * Quality assurance reports, testing checklists, and compliance tracking
  * Data analysis, inventory spreadsheets, vendor comparison, and procurement analytics
  * Cross-departmental meeting minutes, task coordination, and project scheduling
  * Technical presentations, executive briefings, and employee skills development
- Always reinforce that confidential or internal company data must NEVER be uploaded to external AI services.

## EDITORIAL TONE & ANTI-REPETITION MANDATE (STRICT ZERO REDUNDANCY)
1. Single Tool Title: The tool name must only appear ONCE in the main title. Do not repeat it in secondary badge boxes.
2. Zero Overlap Between Page 1 and Page 2:
   - Page 1 covers: Plain English Overview, 5 Key Capabilities, 3-Step User Workflow, Where It Helps, and At-A-Glance Impact.
   - Page 2 MUST NOT repeat the Page 1 steps or time savings. Page 2 covers:
     * Enterprise Integration Architecture (supported software, local vs cloud computation)
     * Real-World Case Study (concrete before/after scenario with real input sample and output result)
     * Data Governance Matrix (permitted unclassified inputs vs prohibited restricted inputs)
     * Enterprise FAQ (data privacy, offline capabilities, human verification protocols)
3. Adaptive Tool Interfaces (NO "N/A" Prompts!):
   - If the tool is chat/prompt-driven (like NotebookLM, ChatGPT, or Julius): Provide practical copy-pasteable prompt templates.
   - If the tool is an IDE extension, autocomplete tool, or background utility (like Kite or Otter): Provide **Keyboard Shortcuts, Workflow Triggers, and Configuration Tips** instead of saying "N/A"!

## Required JSON Schema
{{
  "name": "{tool_name}",
  "category": "<e.g. AI Coding & Automation | AI Data Analysis & Spreadsheets | AI Documentation Assistant>",
  "overview": "<2-3 sentence plain-English elevator pitch explaining what the tool is and why an employee should care without techno-jargon>",
  "what_it_does": "<3-4 rich sentences describing the workplace problem solved, source materials used, and tangible outputs produced>",
  "key_features": [
    "<Feature 1 Title>: <Clear 1-2 sentence explanation of capability 1>",
    "<Feature 2 Title>: <Clear 1-2 sentence explanation of capability 2>",
    "<Feature 3 Title>: <Clear 1-2 sentence explanation of capability 3>",
    "<Feature 4 Title>: <Clear 1-2 sentence explanation of capability 4>",
    "<Feature 5 Title>: <Clear 1-2 sentence explanation of capability 5>"
  ],
  "how_it_works": "<2 sentence clear explanation of the user journey from input to result>",
  "how_it_works_steps": [
    {{
      "step": "01",
      "title": "<Specific Step 1 Action Title, e.g. Open Workspace or Connect Document>",
      "desc": "<1-2 clear sentences explaining what the user inputs or provides>"
    }},
    {{
      "step": "02",
      "title": "<Specific Step 2 Action Title, e.g. AI Pattern Analysis & Synthesis>",
      "desc": "<1-2 clear sentences explaining how the AI processes the data>"
    }},
    {{
      "step": "03",
      "title": "<Specific Step 3 Action Title, e.g. Review, Apply & Export>",
      "desc": "<1-2 clear sentences explaining how the employee reviews and exports the deliverable>"
    }}
  ],
  "where_it_helps": [
    {{
      "icon": "<single emoji e.g. 📊, 📝, 🔍, ⚙️, 💻, 📑, 📋>",
      "title": "<Domain 1 Title, e.g. Standard Operating Procedures>",
      "desc": "<1-2 sentence concrete workplace scenario>"
    }},
    {{
      "icon": "<single emoji>",
      "title": "<Domain 2 Title, e.g. Procurement & Inventory Data>",
      "desc": "<1-2 sentence concrete workplace scenario>"
    }},
    {{
      "icon": "<single emoji>",
      "title": "<Domain 3 Title, e.g. Quality Assurance Tracking>",
      "desc": "<1-2 sentence concrete workplace scenario>"
    }}
  ],
  "feature_snapshot": {{
    "input_badge": "INPUT",
    "input_icon": "📄",
    "input_title": "<Specific input type e.g. Source Files or Plain Text Query>",
    "input_desc": "<Concise description of input>",
    "ai_step_badge": "AI STEP",
    "ai_step_icon": "⚡",
    "ai_step_title": "<Core AI action e.g. Context Analysis & Autocomplete>",
    "ai_step_desc": "<Concise description of AI action>",
    "output_badge": "OUTPUT",
    "output_icon": "📊",
    "output_title": "<Deliverable e.g. Clean Output Code or Verified Summary>",
    "output_desc": "<Concise description of deliverable>",
    "key_advantage": "<1 punchy sentence highlighting the main time-saving or accuracy advantage>"
  }},
  "impact_metrics": {{
    "time_saved": "<e.g. ~4 to 6 hrs/week on routine development or data tasks>",
    "key_metric": "<e.g. Up to 80% faster draft turnaround>",
    "target_departments": "<e.g. Software, Documentation, Quality Assurance, Procurement>",
    "learning_curve": "<e.g. Low (Immediate use in existing tools)>"
  }},
  "practical_applications": "<2-3 sentence overview of practical applications across engineering and enterprise administration>",
  "hal_use_case": "<2-3 sentence safe enterprise application for HAL employees, focusing on documentation, data, or project coordination (NO military program names)>",
  "hal_example_workflow": "<1 sentence concrete daily work example, e.g. Generating standardized inspection checklists from equipment guidelines>",
  "adaptive_workflow": {{
    "label": "<e.g. PROMPT TEMPLATE or KEYBOARD SHORTCUTS & CONFIGURATION>",
    "standard_title": "<e.g. ROUTINE TASK or PRIMARY TRIGGER>",
    "standard_body": "<The copy-paste prompt OR the key combination/trigger phrase to use>",
    "advanced_title": "<e.g. ADVANCED WORKFLOW or POWER-USER CONFIGURATION>",
    "advanced_body": "<The advanced multi-step prompt OR advanced settings tweak>"
  }},
  "page_2_dossier": {{
    "integration_architecture": {{
      "environment": "<Supported tools e.g. VS Code, PyCharm, Chrome, Edge, Excel, Desktop App>",
      "computation_model": "<e.g. Local on-device execution (no cloud transmission) OR Secure HTTPS enterprise cloud>",
      "file_formats": "<e.g. .py, .js, .pdf, .docx, .xlsx, .csv>",
      "setup_instructions": "<2-3 sentence clear technical guide on how to configure and activate the tool>"
    }},
    "case_study": {{
      "title": "<Realistic internal enterprise scenario title>",
      "context": "<The workplace challenge faced by the team>",
      "input_sample": "<Specific sample input data or text used>",
      "ai_transformation": "<How the tool processed or synthesized the input>",
      "final_deliverable": "<The clean resulting output table or formatted document>"
    }},
    "governance_matrix": {{
      "permitted_data": [
        "<Permitted item 1 e.g. Public equipment manuals and vendor datasheets>",
        "<Permitted item 2 e.g. Generic administrative meeting action items>",
        "<Permitted item 3 e.g. Non-sensitive open-source or utility code scripts>"
      ],
      "prohibited_data": [
        "<Prohibited item 1 e.g. Classified defence project parameters or aircraft telemetry>",
        "<Prohibited item 2 e.g. Proprietary design schematics, CAD drawings, or ITAR files>",
        "<Prohibited item 3 e.g. Internal credentials, passwords, or customer flight data>"
      ]
    }},
    "enterprise_faq": [
      {{
        "q": "Does this tool retain or train on uploaded company data?",
        "a": "<Clear, verified enterprise privacy policy answer>"
      }},
      {{
        "q": "Can employees use this tool offline or on closed internal workstations?",
        "a": "<Clear answer on offline/air-gapped availability vs cloud requirement>"
      }},
      {{
        "q": "What is the mandatory human review protocol before sharing outputs?",
        "a": "All AI outputs must be validated by a qualified employee prior to formal team release."
      }}
    ]
  }},
  "website": "{website}",
  "website_display": "<clean domain e.g. julius.ai or kite.com>",
  "pricing_tier": "<one of: Free | Freemium | Paid | Enterprise>",
  "pricing_details": "<Concise pricing summary e.g. 'Free basic tier; Pro plan available for advanced features'>",
  "security_note": "⚠ Do not upload classified, proprietary, or project-sensitive company data to external AI platforms. Verify IT guidelines before use. — HAL IT Security"
}}
Return ONLY the raw JSON object. No markdown backticks, no preamble.
""")
