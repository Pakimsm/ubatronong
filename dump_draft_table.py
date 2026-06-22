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
    await login_page.login(account.email, account.password)
    
    await page.goto("https://www.soundon.global/library/list?lang=id&type=drafts")
    await asyncio.sleep(5)
    
    # Dump the HTML of the action icons or table rows
    html = await page.evaluate('''() => {
        const rows = [...document.querySelectorAll('tr')];
        return rows.map(r => r.outerHTML);
    }''')
    
    print(f"Found {len(html)} rows:")
    for i, row in enumerate(html):
        print(f"\n--- Row {i} ---")
        print(row)
        
    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
