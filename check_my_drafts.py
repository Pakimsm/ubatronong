import asyncio
from pathlib import Path
from src.core.browser import PlaywrightBrowser
from src.core.account_manager import JsonAccountRepository
from src.models.browser_config import BrowserConfig
from src.pages.login import LoginPage

async def main():
    config = BrowserConfig(headless=True)
    browser = PlaywrightBrowser(config)
    await browser.launch()
    
    account_repo = JsonAccountRepository(Path("config/accounts.json"))
    account = next(a for a in account_repo.get_all() if a.email == "tgobox.jkt.1747@gmail.com")
    
    page = await browser.new_page()
    login_page = LoginPage(page)
    print("Logging in...")
    logged_in = await login_page.login(account.email, account.password)
    print(f"Logged in: {logged_in}")
    
    print("Navigating to drafts page...")
    await page.goto("https://www.soundon.global/library/list?type=drafts")
    await asyncio.sleep(5)
    
    # Take screenshot of drafts
    await page.screenshot(path="drafts_final.png", full_page=True)
    print("Saved screenshot to drafts_final.png")
    
    # Get all text
    text = await page.evaluate("document.body.innerText")
    print("--- Drafts Page Content ---")
    print(text[:2000])
    print("---------------------------")
    
    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
