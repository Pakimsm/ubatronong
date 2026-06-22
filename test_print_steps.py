import asyncio
from pathlib import Path
from src.core.browser import PlaywrightBrowser
from src.core.account_manager import JsonAccountRepository
from src.models.browser_config import BrowserConfig
from src.pages.login import LoginPage
from src.pages.lagu_publish import LaguPublishPage
from src.models.upload_payload import UploadPayload

async def main():
    config = BrowserConfig(headless=True)
    browser = PlaywrightBrowser(config)
    await browser.launch()
    page = await browser.new_page()
    
    account_repo = JsonAccountRepository(Path("config/accounts.json"))
    target_account = next(a for a in account_repo.get_all() if a.email == "tgobox.jkt.1747@gmail.com")
    
    # Login
    login_page = LoginPage(page)
    await login_page.login(target_account.email, target_account.password)
    
    # Go to single publish
    publish_page = LaguPublishPage(page)
    await publish_page.go_to_single_publish()
    print("URL after go_to_single_publish:", await page.current_url())
    
    payload = UploadPayload(
        track_path=Path("/home/aaa/Downloads/Jane_Eyre_Songs/Fire Stone/Fire In The Bed.wav"),
        title="Fire In The Bed",
        artist="Kurs",
        genre="Pop",
        songwriter_name="Kusriyah"
    )
    
    # We will step through fill_track_information manually to see the URLs
    await page.set_input_files("input[type='file'][accept*='.mp3']", str(payload.track_path))
    print("URL after set_input_files:", await page.current_url())
    
    # Wait for inputs to appear
    print("Waiting for input[type='text']...")
    await page._page.wait_for_selector("input[type='text']", state="visible", timeout=1800000)
    print("URL after input[type='text'] is visible:", await page.current_url())
    
    # Let's take a screenshot right now to see if we are on Step 1
    await page._page.screenshot(path="debug_step1.png", full_page=True)
    print("Saved debug_step1.png. URL is:", await page.current_url())
    
    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
