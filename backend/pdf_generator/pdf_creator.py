"""PDF generation using Playwright (Chromium headless)."""

import asyncio
import base64
import io
import os
import sys
from pathlib import Path

import qrcode
from playwright.async_api import async_playwright

from backend.template_engine.html_renderer import HTMLRenderer
from backend.config.settings import settings


def _render_pdf_sync(html: str, output_path: str):
    """
    Render PDF inside an isolated event loop with WindowsProactorEventLoopPolicy.
    Prevents NotImplementedError when uvicorn reloader runs on SelectorEventLoop.
    """
    async def _runner():
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.set_content(html, wait_until="networkidle")
            await page.pdf(
                path=output_path,
                format="A4",
                print_background=True,
                margin={
                    "top": "0mm",
                    "bottom": "0mm",
                    "left": "0mm",
                    "right": "0mm",
                },
            )
            await browser.close()

    if sys.platform == "win32":
        loop = asyncio.WindowsProactorEventLoopPolicy().new_event_loop()
    else:
        loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_runner())
    finally:
        loop.close()


class PDFCreator:
    """Renders newsletter HTML and exports to A4 PDF via Playwright."""

    def __init__(self):
        self.renderer = HTMLRenderer(settings.templates_dir)

    # ------------------------------------------------------------------
    # QR code helper
    # ------------------------------------------------------------------

    def _make_qr_b64(self, url: str) -> str:
        """Generate a base64-encoded PNG QR code data URI."""
        qr = qrcode.QRCode(version=1, box_size=4, border=1)
        qr.add_data(url if url else "https://hal-india.co.in")
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return "data:image/png;base64," + base64.b64encode(buf.read()).decode()

    # ------------------------------------------------------------------
    # Main PDF generation
    # ------------------------------------------------------------------

    async def generate_pdf(
        self,
        tools_data: list,
        issue_info: dict,
        output_path: str,
        template_name: str = "classic",
    ) -> str:
        """
        Generate a PDF newsletter.

        Args:
            tools_data: list of tool content dicts (each becomes one A4 page)
            issue_info: dict with issue_number, week_label, pub_date, title
            output_path: destination .pdf file path
            template_name: "classic" | "modern"

        Returns:
            Absolute path to the generated PDF.
        """
        # 1. Attach QR code to each tool
        for tool in tools_data:
            tool["qr_code_b64"] = self._make_qr_b64(tool.get("website", ""))

        # Attach official HAL logo base64 if present
        logo_file = Path("templates/hal_logo.b64")
        if logo_file.exists():
            issue_info["hal_logo_b64"] = logo_file.read_text(encoding="utf-8").strip()

        # 2. Render Jinja2 → HTML
        html = self.renderer.render_newsletter(
            tools_data, issue_info, template_name=template_name
        )

        # 3. Save debug HTML alongside PDF
        html_path = output_path.replace(".pdf", ".html")
        Path(html_path).write_text(html, encoding="utf-8")

        # 4. Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # 5. Launch Playwright in dedicated thread with Proactor loop
        await asyncio.to_thread(_render_pdf_sync, html, output_path)

        return str(Path(output_path).resolve())
