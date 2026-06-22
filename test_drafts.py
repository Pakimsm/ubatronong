import asyncio
from playwright.async_api import async_playwright
from src.utils.session_manager import SessionManager
import os

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        session_manager = SessionManager(browser)
        page = await session_manager.get_session("tgobox.jkt.1747@gmail.com")
        
        print("Navigating to drafts page...")
        await page._page.goto("https://www.soundon.global/library/list?lang=id&type=drafts", wait_until="networkidle")
        await asyncio.sleep(5)
        
        await page._page.screenshot(path="drafts_screenshot.png", full_page=True)
        print("Screenshot saved to drafts_screenshot.png")
        
        # Get all text
        text = await page._page.evaluate("document.body.innerText")
        
        if "Fire Stone" in text:
            print("Found Fire Stone in the page text!")
        else:
            print("Could not find Fire Stone in the page text.")
            
        await browser.close()

asyncio.run(main())
