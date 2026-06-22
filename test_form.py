import asyncio
from pathlib import Path
import src.cli.app
from src.core.browser import PlaywrightBrowser
from src.core.account_manager import JsonAccountRepository
from src.models.browser_config import BrowserConfig
from src.models.upload_payload import UploadPayload
from src.pages.login import LoginPage
from src.pages.album_publish import AlbumPublishPage

async def test_form():
    config = BrowserConfig(headless=True)
    browser = PlaywrightBrowser(config)
    await browser.launch()
    page = await browser.new_page()
    
    account_repo = JsonAccountRepository(Path("config/accounts.json"))
    account = account_repo.get_all()[0]
    
    login_page = LoginPage(page)
    await login_page.login(account.email, account.password)
    
    publish_page = AlbumPublishPage(page)
    await publish_page.go_to_album_publish()
    
    # Dismiss ads
    try:
        await publish_page.wait_for_element("button:has-text('Nanti saja'), .semi-modal-close, button:has-text('Tutup')", timeout=6000)
        await publish_page.page.click("button:has-text('Nanti saja'), .semi-modal-close, button:has-text('Tutup')")
        await asyncio.sleep(1)
    except Exception:
        pass
    await publish_page.dismiss_popups()
    await asyncio.sleep(1)
    
    p = publish_page.page._page
    print("DEBUG: Clicking Genre dropdown via Tab...")
    # Click the Genre label, then press Tab to focus the dropdown, then Enter to open it
    await p.locator("text='Genre'").first.click(force=True)
    await p.keyboard.press("Tab")
    await asyncio.sleep(0.5)
    await p.keyboard.press("Enter")
    await asyncio.sleep(1)
    
    print("DEBUG: Taking screenshot of opened dropdown...")
    await p.screenshot(path="/home/aaa/soundonbot/debug_genre_open.png", full_page=True)
    
    print("DEBUG: Typing into the search input...")
    await p.fill("input[class*='search'], input[type='text']:visible >> nth=-1", "Pop")
    await asyncio.sleep(1)
    
    print("DEBUG: Taking screenshot of filtered dropdown...")
    await p.screenshot(path="/home/aaa/soundonbot/debug_genre_typed.png", full_page=True)
    
    print("DEBUG: Clicking the first option...")
    await p.locator("[class*='option'], [class*='dropdown'] li").first.click()
    await asyncio.sleep(1)
    
    print("DEBUG: Taking screenshot after selecting Genre...")
    await p.screenshot(path="/home/aaa/soundonbot/debug_genre_selected.png", full_page=True)
    
    await browser.close()

if __name__ == "__main__":
    asyncio.run(test_form())
