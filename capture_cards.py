import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

async def capture_cards():
    artifact_dir = Path("C:/Users/VICTUS/.gemini/antigravity/brain/72eb48a7-7a29-4e5b-bfa8-663dc8667c6b")

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1440, "height": 1100})
        await page.goto("http://localhost:5173/", wait_until="networkidle")
        await page.wait_for_timeout(1000)

        # Scroll to review section
        review_el = await page.query_selector(".review-section")
        if review_el:
            await review_el.scroll_into_view_if_needed()
            await page.wait_for_timeout(500)
            await page.screenshot(path=str(artifact_dir / "dashboard_tool_cards.png"))
            print("Captured dashboard_tool_cards.png")
        else:
            print("Review section not found.")

        await browser.close()

asyncio.run(capture_cards())
