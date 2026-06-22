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
    page = await browser.new_page()
    
    account_repo = JsonAccountRepository(Path("config/accounts.json"))
    target_account = next(a for a in account_repo.get_all() if a.email == "tgobox.jkt.1747@gmail.com")
    
    # Login
    login_page = LoginPage(page)
    await login_page.login(target_account.email, target_account.password)
    
    # Go to publish single url
    print("Navigating to single publish page...")
    await page.goto("https://www.soundon.global/library/publish/single?lang=id&region=ID")
    await asyncio.sleep(5)
    
    # Get current url
    url = await page.current_url()
    print("Current URL after navigation:", url)
    
    # Screenshot
    await page.screenshot(path="debug_single_publish_start.png", full_page=True)
    print("Saved debug_single_publish_start.png")
    
    # Check if there are any modals or buttons for resuming
    dialogs = await page.evaluate('''() => {
        const dialogs = [...document.querySelectorAll("dialog, .semi-modal, .so-form-modal-dialog, [class*='modal']")];
        return dialogs.map(d => ({
            className: d.className,
            innerText: d.innerText
        }));
    }''')
    print("Dialogs/modals on screen:", dialogs)
    
    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
