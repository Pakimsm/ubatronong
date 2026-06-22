import asyncio
from playwright.async_api import async_playwright
import json

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            storage_state="data/auth/tgobox.jkt.1747@gmail.com_auth.json",
            viewport={'width': 1280, 'height': 800}
        )
        page = await context.new_page()
        
        print("Navigating to draft...")
        await page.goto("https://www.soundon.global/library/publish/album?source=draft&id=7652210850094319632")
        await asyncio.sleep(15)
        
        await page.screenshot(path="draft_view.png", full_page=True)
        print("Saved draft_view.png")
        await browser.close()

asyncio.run(main())
