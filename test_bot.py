import asyncio
from pathlib import Path
import src.cli.app
from src.core.browser import PlaywrightBrowser
from src.core.account_manager import JsonAccountRepository
from src.models.browser_config import BrowserConfig
from src.models.upload_payload import UploadPayload
from src.pages.login import LoginPage
from src.pages.album_publish import AlbumPublishPage

async def test_album():
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
    print("DEBUG: Waiting for possible ad popups...")
    try:
        await publish_page.wait_for_element("button:has-text('Nanti saja'), .semi-modal-close, button:has-text('Tutup')", timeout=6000)
        print("DEBUG: Found popup, dismissing it.")
        await publish_page.page.click("button:has-text('Nanti saja'), .semi-modal-close, button:has-text('Tutup')")
        await asyncio.sleep(1)
    except Exception:
        pass
    await publish_page.dismiss_popups()
    await asyncio.sleep(1)
    
    print("DEBUG: Taking screenshot of the page before Step 1...")
    await publish_page.page.screenshot("/home/aaa/soundonbot/debug_step1.png", full_page=True)
    
    # Fill Title
    await publish_page.fill_react("input[name*='title' i], input[placeholder*='title' i], input[placeholder*='judul' i], input[type='text'] >> nth=0", "Test Title")
    
    print("DEBUG: Taking screenshot before Step 4 Genre...")
    await publish_page.page.screenshot("/home/aaa/soundonbot/debug_step4.png", full_page=True)
    
    await browser.close()
    print("Done!")

if __name__ == "__main__":
    asyncio.run(test_album())
