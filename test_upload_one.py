import asyncio
from pathlib import Path
from src.core.browser import PlaywrightBrowser
from src.core.account_manager import JsonAccountRepository
from src.models.browser_config import BrowserConfig
from src.tasks.upload_lagu import UploadLaguTask
from src.models.upload_payload import UploadPayload

async def main():
    config = BrowserConfig(headless=True)
    browser = PlaywrightBrowser(config)
    await browser.launch()
    page = await browser.new_page()
    
    account_repo = JsonAccountRepository(Path("config/accounts.json"))
    account = next(a for a in account_repo.get_all() if a.email == "tgobox.jkt.1747@gmail.com")
    
    track_path = "/home/aaa/Downloads/Jane_Eyre_Songs/Fire Stone/Frozen Pitchers.wav"
    payload = UploadPayload(
        track_path=Path(track_path),
        title="Frozen Pitchers Test",
        artist="Kurs",
        genre="Pop",
        songwriter_name="Kusriyah"
    )
    
    task = UploadLaguTask(payload)
    print(f"Uploading song: {payload.title}")
    result = await task.execute(page, account)
    print(f"Result success: {result.success}, Message: {result.message}")
    
    # Save final page state
    await page.screenshot(path="frozen_pitchers_final.png", full_page=True)
    print("Saved frozen_pitchers_final.png")
    
    # Check drafts page
    print("Navigating to drafts page...")
    await page._page.goto("https://www.soundon.global/library/list?lang=id&type=drafts")
    await asyncio.sleep(5)
    
    await page.screenshot(path="drafts_after_frozen.png", full_page=True)
    print("Saved drafts_after_frozen.png")
    
    # Dump drafts list text
    text = await page.evaluate("document.body.innerText")
    print("--- Drafts List Content ---")
    print(text[:2000])
    print("---------------------------")
    
    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
