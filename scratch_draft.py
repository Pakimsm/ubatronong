import asyncio
from pathlib import Path
from src.core.browser import PlaywrightBrowser
from src.core.account_manager import JsonAccountRepository
from src.models.browser_config import BrowserConfig
from src.pages.base import BasePage

async def main():
    config = BrowserConfig(headless=True)
    browser = PlaywrightBrowser(config)
    await browser.launch()
    page = await browser.new_page()
    
    account_repo = JsonAccountRepository(Path("config/accounts.json"))
    accounts = account_repo.get_all()
    target_account = next(a for a in accounts if a.email == "tgobox.jkt.1747@gmail.com")
    
    # Load cookies using BasePage utility
    base_page = BasePage(page)
    # The login mechanism might require navigating first to a domain so cookies can be set
    await page._page.goto("https://www.soundon.global")
    # BasePage.load_state() or login logic
    from src.tasks._base import _BASE
    # actually, BaseTask handles session loading...
    from src.tasks.upload_album import UploadAlbumTask
    from src.models.upload_payload import UploadPayload
    
    # Let's just run UploadAlbumTask but we'll modify it dynamically to just go to the URL and exit
    class DraftTask(UploadAlbumTask):
        async def execute(self, page, account):
            await self._login(page, account)
            print("Navigating to user's draft...")
            await page._page.goto("https://www.soundon.global/library/publish/album?source=draft&id=7652210850094319632", wait_until="networkidle")
            await asyncio.sleep(10)
            await page._page.screenshot(path="draft_investigation.png", full_page=True)
            print("Saved draft_investigation.png")
            return True

    payload = UploadPayload(
        track_path=Path("."), cover_path=None, title="", title_language="", genre="", artist="", release_date=""
    )
    task = DraftTask(payload)
    await task.execute(page, target_account)
    await browser.close()

asyncio.run(main())
