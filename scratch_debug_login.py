import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.browser import PlaywrightBrowser
from src.models.browser_config import BrowserConfig
from src.models.account import Account
from src.modules._base import SoundOnTask, _BASE

class DummyTask(SoundOnTask[str]):
    async def execute(self, page, account):
        print("Start login...")
        await self._login(page, account)
        print(f"Login finished. URL: {page.url}")
        
        await asyncio.sleep(4)
        print(f"URL after sleep: {page.url}")
        return "OK"

async def main():
    config = BrowserConfig(headless=True)
    browser = PlaywrightBrowser(config)
    async with browser:
        page = await browser.new_page()
        task = DummyTask()
        acc = Account(id=99, email="jembut@gmail.com", password="kontol")
        try:
            await task.execute(page, acc)
            print("EXECUTE SUCCESS")
        except Exception as e:
            print(f"EXECUTE FAILED: {e}")

asyncio.run(main())
