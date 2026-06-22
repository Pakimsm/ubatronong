import asyncio
from pathlib import Path
from src.core.browser import PlaywrightBrowser
from src.models.browser_config import BrowserConfig
from src.core.account_manager import JsonAccountRepository
from src.tasks.upload_lagu import UploadLaguTask
from src.pages.login import LoginPage
from src.pages.lagu_publish import LaguPublishPage
from src.models.upload_payload import UploadPayload

async def main():
    config = BrowserConfig(headless=True)
    browser = PlaywrightBrowser(config)
    await browser.launch()
    repo = JsonAccountRepository(Path("config/accounts.json"))
    account = repo.get_all()[0]
    page = await browser.new_page()
    lp = LoginPage(page)
    await lp.login(account.email, account.password)
    
    pp = LaguPublishPage(page)
    await pp.go_to_single_publish()
    
    print("Uploading audio...")
    await pp.page.set_input_files("input[type='file'][accept*='.mp3']", "/home/aaa/Downloads/Jane_Eyre_Songs/Fire Stone/Fire In The Bed.wav")
    
    print("Waiting for 30 seconds...")
    await asyncio.sleep(30)
    
    print("Dumping HTML...")
    html = await pp.page._page.content()
    with open("debug_test_single.html", "w") as f:
        f.write(html)
        
    print("Taking screenshot...")
    await pp.page._page.screenshot(path="debug_test_single.png", full_page=True)
    
    print("Done!")
    await browser.close()

asyncio.run(main())
