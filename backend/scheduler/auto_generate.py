"""
Standalone scheduler script — runs the full newsletter pipeline and sends
an email notification. Can be triggered by Windows Task Scheduler.

Usage:
    venv\\Scripts\\python backend\\scheduler\\auto_generate.py [--template classic|modern]
"""

import argparse
import asyncio
import logging
import smtplib
import sys
import os
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

# ---------------------------------------------------------------------------
# Bootstrap: load .env BEFORE importing settings and ensure sys.path
# ---------------------------------------------------------------------------
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv(dotenv_path=project_root / "config" / ".env")

# ---------------------------------------------------------------------------
# Logging setup — write to both console and log file
# ---------------------------------------------------------------------------
LOG_DIR = Path("generated_newsletters") / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "scheduler.log"

handlers = [
    logging.StreamHandler(sys.stdout),
    logging.FileHandler(str(LOG_FILE), encoding="utf-8"),
]
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=handlers,
)
logger = logging.getLogger("scheduler")

# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

async def run_pipeline(template_name: str = "classic"):
    from backend.services.research_service import ResearchService
    from backend.services.content_service import ContentService
    from backend.database.db_manager import init_db

    logger.info("=== HAL Newsletter Auto-Generate Started (Template: %s) ===", template_name)

    # Init DB
    await init_db()

    # Research
    research_service = ResearchService()
    logger.info("Starting tool discovery …")
    tools_research = await research_service.run_research_pipeline(count=3)
    if not tools_research:
        logger.error("No tools discovered — aborting.")
        return None

    # Content + PDF
    content_service = ContentService()
    logger.info("Generating content and PDF …")
    result = await content_service.run_content_pipeline(tools_research, template_name=template_name)
    logger.info("Pipeline complete. PDF saved to: %s", result["pdf_path"])
    return result


def send_email_notification(result: dict):
    """Send a notification email to admin when the newsletter is ready."""
    from backend.config.settings import settings

    if not settings.smtp_user or not settings.smtp_password or not settings.admin_email:
        logger.info("Email not configured — skipping notification.")
        return

    try:
        issue = result["issue_info"]
        subject = f"[HAL Newsletter] Issue #{issue['issue_number']} — {issue['week_label']} is ready"
        body = (
            f"Hello,\n\n"
            f"The HAL AI Tools Weekly Newsletter has been generated successfully.\n\n"
            f"Issue: #{issue['issue_number']}\n"
            f"Week: {issue['week_label']}\n"
            f"Date: {issue['pub_date']}\n"
            f"Template: {result.get('issue_info', {}).get('template_name', 'classic')}\n"
            f"PDF: {result['pdf_path']}\n\n"
            f"Preview at: {settings.base_url}/api/newsletter/{result['newsletter_id']}/preview\n\n"
            f"— HAL Newsletter Bot"
        )

        msg = MIMEMultipart()
        msg["From"] = settings.smtp_user
        msg["To"] = settings.admin_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)

        logger.info("Email notification sent to %s", settings.admin_email)

    except Exception as exc:
        logger.error("Failed to send email: %s", exc)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auto-generate HAL AI Newsletter")
    parser.add_argument("--template", default="classic", choices=["classic", "modern"], help="Design template to use")
    args = parser.parse_args()

    result = asyncio.run(run_pipeline(template_name=args.template))
    if result:
        send_email_notification(result)
        logger.info("=== Scheduler finished successfully ===")
    else:
        logger.error("=== Scheduler finished with errors ===")
        sys.exit(1)
