import asyncio
from pathlib import Path
from src.core.browser import PlaywrightBrowser
from src.core.account_manager import JsonAccountRepository
from src.models.browser_config import BrowserConfig
from src.models.upload_payload import UploadPayload
from src.tasks.upload_lagu import UploadLaguTask
from src.pages.login import LoginPage
from src.pages.lagu_publish import LaguPublishPage

async def test_lagu():
    config = BrowserConfig(headless=True)
    browser = PlaywrightBrowser(config)
    await browser.launch()
    
    account_repo = JsonAccountRepository(Path("config/accounts.json"))
    accounts = account_repo.get_all()
    account = next((a for a in accounts if a.email == "tgobox.jkt.1747@gmail.com"), None)
    
    payload = UploadPayload(
        track_path=Path("/home/aaa/Downloads/Jane_Eyre_Songs/Fire Stone/Fire In The Bed.wav"),
        title="Fire In The Bed",
        artist="Kurs",
        genre="Pop",
        songwriter_name="Kusriyah"
    )
    
    page = await browser.new_page()
    login_page = LoginPage(page)
    await login_page.login(account.email, account.password)

    publish_page = LaguPublishPage(page)
    await publish_page.go_to_single_publish()
    await publish_page.fill_track_information(payload)
    await publish_page.fill_release_settings(payload)
    await publish_page.skip_more_options()
    
    print("Dumping screenshot before clicking draft...")
    await page._page.screenshot(path="/home/aaa/soundonbot/debug_predraft.png", full_page=True)
    html = await page._page.content()
    with open("/home/aaa/soundonbot/debug_predraft_new.html", "w") as f:
        f.write(html)
    print("Done dumping HTML.")

if __name__ == "__main__":
    asyncio.run(test_lagu())
