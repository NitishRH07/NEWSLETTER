import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

async def render():
    html_path = Path("generated_newsletters/HAL_AI_Tools_Weekly_Issue07_20261117.html").resolve()
    artifact_dir = Path("C:/Users/VICTUS/.gemini/antigravity/brain/72eb48a7-7a29-4e5b-bfa8-663dc8667c6b")

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1200, "height": 1600})
        await page.goto(f"file:///{html_path.as_posix()}", wait_until="networkidle")

        pages = await page.query_selector_all(".page")
        print(f"Found {len(pages)} pages.")

        for i, page_el in enumerate(pages, 1):
            out_img = artifact_dir / f"issue07_modern_page{i}.png"
            await page_el.screenshot(path=str(out_img))
            print(f"Rendered Page {i} -> {out_img}")

        await browser.close()

asyncio.run(render())
