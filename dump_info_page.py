import asyncio
from src.core.browser import PlaywrightBrowser
from src.models.browser_config import BrowserConfig

async def main():
    config = BrowserConfig(headless=True)
    browser = PlaywrightBrowser(config)
    await browser.launch()
    page = await browser.new_page()
    
    # login
    from src.tasks.upload_album import UploadAlbumTask
    from src.models.upload_payload import UploadPayload
    from pathlib import Path
    from src.core.account_manager import JsonAccountRepository
    
    account_repo = JsonAccountRepository(Path("config/accounts.json"))
    target_account = next(a for a in account_repo.get_all() if a.email == "tgobox.jkt.1747@gmail.com")
    
    class DumpTask(UploadAlbumTask):
        async def execute(self, page, account):
            await self._login(page, account)
            await page._page.goto("https://www.soundon.global/library/publish/album?lang=id&region=ID", wait_until="networkidle")
            await asyncio.sleep(5)
            html = await page._page.content()
            with open("info_page_dump.html", "w") as f:
                f.write(html)
            print("Dumped info_page_dump.html")
            return True

    task = DumpTask(UploadPayload(track_path=Path("."), cover_path=None, title="", title_language="", genre="", artist="", release_date=""))
    await task.execute(page, target_account)
    await browser.close()

asyncio.run(main())
