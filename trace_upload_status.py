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
    
    # Start upload
    print("Starting audio upload...")
    await page.set_input_files("input[type='file'][accept*='.mp3']", str(payload.track_path))
    
    # Trace the status text inside the audio upload area
    for i in range(24): # check every 5 seconds for 2 minutes
        await asyncio.sleep(5)
        status_text = await page.evaluate('''() => {
            // Find the container containing the file name
            const container = [...document.querySelectorAll("div")].find(d => d.innerText && d.innerText.includes("Fire In The Bed.wav"));
            return container ? container.innerText.split("\\n").join(" | ") : "Container not found";
        }''')
        print(f"Time: {5 * (i + 1)}s | Status: {status_text}")
        
        # Take screenshot halfway and end
        if i == 5 or i == 15 or "Berhasil" in status_text or "complete" in status_text.lower():
            await page._page.screenshot(path=f"debug_step4.png", full_page=True)
            
        if "Berhasil" in status_text or "complete" in status_text.lower() or "success" in status_text.lower():
            print("Detected completion!")
            break
            
    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
