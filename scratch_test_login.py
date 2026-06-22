import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.soundon.global/login")
        await page.wait_for_selector("input[name='username']")
        await page.fill("input[name='username']", "jembut@gmail.com")
        await page.fill("input[data-id='password-input']", "kontol")
        
        # Click login
        await page.click("button:has-text('Log in')")
        
        # Wait a bit
        await asyncio.sleep(3)
        
        url = page.url
        content = await page.content()
        print(f"URL after click: {url}")
        
        # Look for error texts
        if "Incorrect" in content or "error" in content.lower():
            print("Found error in content")
        
        await browser.close()

asyncio.run(main())
