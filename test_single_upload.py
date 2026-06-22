import asyncio
from pathlib import Path
import sys
import os

# Add project root to sys.path
sys.path.append("/home/aaa/soundonbot")

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
    
    account_repo = JsonAccountRepository(Path("/home/aaa/soundonbot/config/accounts.json"))
    target_account = next(a for a in account_repo.get_all() if a.email == "tgobox.jkt.1747@gmail.com")
    
    print("Logging in...")
    login_page = LoginPage(page)
    await login_page.login(target_account.email, target_account.password)
    
    print("Navigating to single publish...")
    publish_page = LaguPublishPage(page)
    await publish_page.go_to_single_publish()
    
    # Save a screenshot of the initial page state
    await page.screenshot(path="initial_upload_state.png", full_page=True)
    print("Saved initial_upload_state.png")
    
    track_path = "/home/aaa/Downloads/Jane_Eyre_Songs/Fire Stone/Fire In The Bed.wav"
    payload = UploadPayload(
        track_path=Path(track_path),
        title="Fire In The Bed",
        artist="Kurs",
        genre="Pop",
        songwriter_name="Kusriyah"
    )
    
    print(f"Setting input files for: {track_path}")
    await page.set_input_files("input[type='file'][accept*='.mp3']", str(payload.track_path))
    
    # Let's poll and take screenshots/prints for 90 seconds
    for i in range(18):
        await asyncio.sleep(5)
        elapsed = (i + 1) * 5
        print(f"\n--- Elapsed: {elapsed} seconds ---")
        
        # Take screenshot
        screenshot_name = f"upload_step_{elapsed}s.png"
        await page.screenshot(path=screenshot_name, full_page=True)
        print(f"Saved {screenshot_name}")
        
        # Find upload-related elements/texts on the page
        info = await page.evaluate('''() => {
            // Find all visible texts that look like progress or success
            const allTexts = [...document.querySelectorAll('div, span, p, label')].map(el => el.innerText).filter(t => t && t.trim().length > 0);
            
            // Check for progress indicators or percentages
            const progressTexts = allTexts.filter(t => t.includes('%') || /progress|upload|berhasil|sukses|gagal|error|complete/i.test(t));
            
            // Check file inputs
            const inputs = [...document.querySelectorAll('input[type="file"]')].map(input => ({
                accept: input.accept,
                files: input.files ? [...input.files].map(f => f.name) : []
            }));
            
            return {
                progressTexts: progressTexts.slice(0, 15),
                inputs: inputs
            };
        }''')
        
        print("Progress/Status Texts found:", info["progressTexts"])
        print("File inputs status:", info["inputs"])
        
    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
