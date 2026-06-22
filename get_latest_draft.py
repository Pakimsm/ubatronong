import asyncio
from pathlib import Path
from src.core.browser import PlaywrightBrowser
from src.core.account_manager import JsonAccountRepository
from src.models.browser_config import BrowserConfig
from src.tasks.upload_album import UploadAlbumTask
from src.models.upload_payload import UploadPayload

async def main():
    config = BrowserConfig(headless=True)
    browser = PlaywrightBrowser(config)
    await browser.launch()
    page = await browser.new_page()
    
    account_repo = JsonAccountRepository(Path("config/accounts.json"))
    target_account = next(a for a in account_repo.get_all() if a.email == "tgobox.jkt.1747@gmail.com")
    
    class DraftTask(UploadAlbumTask):
        async def execute(self, page, account):
            await self._login(page, account)
            await page._page.goto("https://www.soundon.global/library/list?lang=id&type=drafts", wait_until="networkidle")
            await asyncio.sleep(5)
            
            # Click the FIRST edit button
            await page._page.locator("a[href*='source=draft']").first.click()
            await asyncio.sleep(10)
            
            await page._page.screenshot(path="new_draft_edit.png", full_page=True)
            print("Saved new_draft_edit.png")
            return True

    task = DraftTask(UploadPayload(track_path=Path("."), cover_path=None, title="", title_language="", genre="", artist="", release_date=""))
    await task.execute(page, target_account)
    await browser.close()

asyncio.run(main())
