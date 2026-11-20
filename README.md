# HAL AI Tools Weekly — Newsletter Generator

A full-stack automated newsletter generator for **Hindustan Aeronautics Limited (HAL)**, producing a professional A4 PDF newsletter featuring three AI tools per week — complete with AI-written content, QR codes, and an aerospace-themed design.

---

## 🏗 Architecture

```
React (Vite) Frontend  ←→  FastAPI Backend  ←→  SQLite DB
                                   ↕
                          Gemini AI (content)
                          DuckDuckGo / SerpAPI (research)
                          Playwright (HTML → PDF)
```

---

## 📋 Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Python | 3.11+ | [python.org](https://python.org) |
| Node.js | 18+ | [nodejs.org](https://nodejs.org) |
| Git | Any | [git-scm.com](https://git-scm.com) |

---

## ⚡ Quick Start (Windows)

### 1. Clone / Download

```bat
cd d:\Hobby
git clone <repo-url> AI_NEWSLETTER
cd AI_NEWSLETTER
```

### 2. Run Setup

```bat
setup.bat
```

This will:
- Create a Python virtual environment (`venv\`)
- Install all Python dependencies from `backend\requirements.txt`
- Download Playwright Chromium browser
- Initialise the SQLite database

### 3. Configure API Keys

Edit `config\.env` (created by setup.bat from the example):

```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
SEARCH_ENGINE=duckduckgo          # or serpapi
SEARCH_API_KEY=                   # only needed for serpapi
ADMIN_EMAIL=your@email.com        # for email notifications
SMTP_USER=your@gmail.com
SMTP_PASSWORD=your_app_password
```

> **Getting a Gemini API Key:**
> 1. Go to [aistudio.google.com](https://aistudio.google.com)
> 2. Click "Get API Key" → Create API key
> 3. Paste it into `config\.env`

### 4. Test with Sample PDF (no API key needed)

```bat
venv\Scripts\python backend\sample_data.py
```

Opens `generated_newsletters\SAMPLE_HAL_AI_Tools_Weekly.pdf`

---

## 🚀 Running the Application

### Backend (FastAPI)

```bat
run_backend.bat
```

API available at: `http://localhost:8000`  
Swagger docs at: `http://localhost:8000/docs`

### Frontend (React/Vite)

```bat
run_frontend.bat
```

App available at: `http://localhost:5173`

---

## 📁 Project Structure

```
AI_NEWSLETTER/
├── backend/
│   ├── api/
│   │   └── routes/
│   │       ├── newsletter.py      # Newsletter CRUD + generate endpoints
│   │       ├── settings.py        # App settings API
│   │       └── history.py         # Published tools history
│   ├── config/
│   │   └── settings.py            # Pydantic settings (loads config/.env)
│   ├── content_generation/
│   │   ├── gemini_client.py       # Gemini API wrapper
│   │   ├── prompt_templates.py    # Structured prompts
│   │   └── content_generator.py  # Orchestrates generation + JSON validation
│   ├── database/
│   │   ├── models.py              # SQLAlchemy ORM models
│   │   └── db_manager.py         # Async session manager + init_db()
│   ├── pdf_generator/
│   │   └── pdf_creator.py        # QR codes + Playwright PDF export
│   ├── research/
│   │   ├── web_search.py          # DuckDuckGo / SerpAPI backends
│   │   ├── tool_researcher.py    # Tool discovery + deep research
│   │   └── verifier.py           # Website liveness verification
│   ├── scheduler/
│   │   └── auto_generate.py      # Standalone script for Task Scheduler
│   ├── services/
│   │   ├── research_service.py   # Research pipeline orchestrator
│   │   └── content_service.py    # Content + PDF + DB orchestrator
│   ├── template_engine/
│   │   └── html_renderer.py      # Jinja2 HTML renderer
│   ├── main.py                   # FastAPI app entry point
│   ├── requirements.txt          # Python dependencies
│   └── sample_data.py            # Sample PDF generator (no API needed)
├── config/
│   ├── .env                      # Your actual config (gitignored)
│   └── .env.example              # Template
├── frontend/
│   ├── src/
│   │   ├── components/            # React components
│   │   ├── pages/                 # Page-level components
│   │   └── services/              # API client utilities
│   ├── package.json
│   └── vite.config.js
├── generated_newsletters/         # Output: PDFs, HTMLs, JSONs
│   └── logs/
│       └── scheduler.log
├── templates/
│   └── newsletter_page.html       # Jinja2 A4 newsletter template
├── tests/
├── setup.bat                      # One-time setup
├── run_backend.bat               # Start FastAPI
└── run_frontend.bat              # Start Vite dev server
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/newsletter/generate` | Trigger full pipeline |
| `GET` | `/api/newsletter/generate/status` | Poll generation status |
| `GET` | `/api/newsletter/list` | List all newsletters |
| `GET` | `/api/newsletter/{id}` | Newsletter detail |
| `GET` | `/api/newsletter/{id}/preview` | HTML preview in browser |
| `GET` | `/api/newsletter/{id}/download` | Download PDF |
| `PUT` | `/api/newsletter/{id}/approve` | Approve newsletter |
| `POST` | `/api/newsletter/{id}/regenerate-tool/{n}` | Regenerate one tool |
| `GET` | `/api/settings` | View settings |
| `PUT` | `/api/settings` | Update settings |
| `GET` | `/api/history/tools` | List published tools |

---

## 🕒 Weekly Automation (Windows Task Scheduler)

### Setup steps:

1. Open **Task Scheduler** (`taskschd.msc`)
2. Click **Create Basic Task** → Name it `HAL Newsletter Weekly`
3. **Trigger**: Weekly → Select day (e.g., Monday) → Time: 08:00
4. **Action**: Start a Program
   - Program: `d:\Hobby\AI_NEWSLETTER\venv\Scripts\python.exe`
   - Arguments: `backend\scheduler\auto_generate.py`
   - Start in: `d:\Hobby\AI_NEWSLETTER`
5. Click **Finish**
6. Right-click the task → **Properties** → General → ✅ "Run whether user is logged on or not"

The script logs to `generated_newsletters\logs\scheduler.log` and sends an email when done.

---

## 🔧 Manual Pipeline Run

```bat
venv\Scripts\python backend\scheduler\auto_generate.py
```

---

## 🎨 Template Customisation

The newsletter template lives at `templates\newsletter_page.html`.

Key design constants:
- **Navy**: `#003087`
- **Red**: `#CC0000`
- **Font**: Arial/Helvetica (system sans-serif, PDF-safe)
- **Page**: A4 portrait, 210×297mm

To adjust section order or layout, edit the `{% for tool in tools %}` block in the template.

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| `Playwright not found` | Run `venv\Scripts\playwright install chromium` |
| `Gemini API error` | Check `GEMINI_API_KEY` in `config\.env` |
| `ModuleNotFoundError` | Run from project root: `cd d:\Hobby\AI_NEWSLETTER` |
| `Database not found` | Run `venv\Scripts\python backend\database\db_manager.py --init` |
| PDF is blank | Check `generated_newsletters\*.html` debug file in browser |
| DuckDuckGo rate limited | Switch to SerpAPI: set `SEARCH_ENGINE=serpapi` and add key |

---

## 📄 License

Internal HAL use only. Not for public distribution.
