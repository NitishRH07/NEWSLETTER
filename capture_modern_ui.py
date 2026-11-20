import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

async def capture():
    artifact_dir = Path("C:/Users/VICTUS/.gemini/antigravity/brain/72eb48a7-7a29-4e5b-bfa8-663dc8667c6b")

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1440, "height": 950})

        # 1. Dashboard
        await page.goto("http://localhost:5173/", wait_until="networkidle")
        await page.wait_for_timeout(1000)
        await page.screenshot(path=str(artifact_dir / "dashboard_modernized.png"))
        print("Captured dashboard_modernized.png")

        # 2. History
        await page.goto("http://localhost:5173/history", wait_until="networkidle")
        await page.wait_for_timeout(1000)
        await page.screenshot(path=str(artifact_dir / "history_modernized.png"))
        print("Captured history_modernized.png")

        # 3. Settings
        await page.goto("http://localhost:5173/settings", wait_until="networkidle")
        await page.wait_for_timeout(1000)
        await page.screenshot(path=str(artifact_dir / "settings_modernized.png"))
        print("Captured settings_modernized.png")

        # 4. Preview Issue 7
        await page.goto("http://localhost:5173/preview/7", wait_until="networkidle")
        await page.wait_for_timeout(1500)
        await page.screenshot(path=str(artifact_dir / "preview_modernized.png"))
        print("Captured preview_modernized.png")

        await browser.close()

asyncio.run(capture())
