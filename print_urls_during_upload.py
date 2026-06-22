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
    
    payload = UploadPayload(
        track_path=Path("/home/aaa/Downloads/Jane_Eyre_Songs/Fire Stone/Fire In The Bed.wav"),
        title="Fire In The Bed",
        artist="Kurs",
        genre="Pop",
        songwriter_name="Kusriyah"
    )
    
    # Run the upload in the background, but print URLs
    async def monitor_url():
        for i in range(60):
            try:
                print(f"[Monitor] Time: {i*2}s | URL: {await page.current_url()}")
            except:
                pass
            await asyncio.sleep(2)
            
    monitor_task = asyncio.create_task(monitor_url())
    
    # Start upload
    try:
        await publish_page.fill_track_information(payload)
    except Exception as e:
        print(f"Exception during fill_track_information: {e}")
        
    monitor_task.cancel()
    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
