import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            storage_state="src/data/sessions/tgobox.jkt.1747@gmail.com_state.json",
            viewport={'width': 1280, 'height': 800}
        )
        page = await context.new_page()
        print("Navigating to drafts page...")
        await page.goto("https://www.soundon.global/library/list?lang=id&type=drafts", wait_until="networkidle")
        await asyncio.sleep(5)
        
        await page.screenshot(path="drafts_screenshot.png", full_page=True)
        print("Screenshot saved to drafts_screenshot.png")
        
        # Get all text
        text = await page.evaluate("document.body.innerText")
        
        import re
        if "Fire Stone" in text:
            print("Found Fire Stone in the page text!")
        else:
            print("Could not find Fire Stone in the page text.")
            
        await browser.close()

asyncio.run(main())
