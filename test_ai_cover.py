import asyncio
from pathlib import Path
from src.core.browser import PlaywrightBrowser
from src.core.account_manager import JsonAccountRepository
from src.models.browser_config import BrowserConfig
from src.pages.login import LoginPage
from src.tasks._base import _BASE

async def test_cover():
    config = BrowserConfig(headless=True)
    browser = PlaywrightBrowser(config)
    await browser.launch()
    
    account_repo = JsonAccountRepository(Path("config/accounts.json"))
    account = account_repo.get_all()[0]
    
    page = await browser.new_page()
    login_page = LoginPage(page)
    await login_page.login(account.email, account.password)
    
    await page.goto(f"{_BASE}/library/publish/single?lang=id&region=ID")
    await asyncio.sleep(5)
    
    # Click Buat sampul AI
    try:
        await page.click("button:has-text('Buat sampul ai'), button:has-text('Buat sampul AI'), button:has-text('Generate AI cover')")
        await asyncio.sleep(2)
        await page.click("text='Animasi 2D'")
        await asyncio.sleep(1)
        await page.click("button:has-text('Hasilkan'), button:has-text('Generate')")
        
        print("Waiting 20 seconds for generation...")
        await asyncio.sleep(20)
        
        html = await page.content()
        with open("/home/aaa/soundonbot/debug_cover.html", "w") as f:
            f.write(html)
        print("Dumped HTML.")
    except Exception as e:
        print("Error:", e)
    
    await browser.close()

if __name__ == "__main__":
    asyncio.run(test_cover())
