import asyncio
from pathlib import Path
import sys

sys.path.append("/home/aaa/soundonbot")

from src.core.browser import PlaywrightBrowser
from src.core.account_manager import JsonAccountRepository
from src.models.browser_config import BrowserConfig
from src.tasks.upload_lagu import UploadLaguTask
from src.models.upload_payload import UploadPayload

async def main():
    # Use headless=True
    config = BrowserConfig(headless=False)
    browser = PlaywrightBrowser(config)
    await browser.launch()
    page = await browser.new_page()
    
    account_repo = JsonAccountRepository(Path("/home/aaa/soundonbot/config/accounts.json"))
    target_account = next(a for a in account_repo.get_all() if a.email == "tgobox.jkt.1747@gmail.com")
    
    track_path = "/home/aaa/Downloads/Jane_Eyre_Songs/Fire Stone/Fire In The Bed.wav"
    payload = UploadPayload(
        track_path=Path(track_path),
        title="Fire In The Bed Task Test",
        artist="Kurs",
        genre="Pop",
        songwriter_name="Kusriyah"
    )
    
    task = UploadLaguTask(payload)
    print("Executing UploadLaguTask...")
    result = await task.execute(page, target_account)
    
    print(f"Task result: success={result.success}, message={result.message}")
    
    await page.screenshot(path="task_final_state.png", full_page=True)
    print("Saved task_final_state.png")
    
    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
