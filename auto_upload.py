import asyncio
import sys
from pathlib import Path
from src.core.browser import PlaywrightBrowser
from src.core.account_manager import JsonAccountRepository
from src.models.browser_config import BrowserConfig
from src.models.upload_payload import UploadPayload
from src.tasks.upload_lagu import UploadLaguTask
from src.pages.login import LoginPage
from src.pages.lagu_publish import LaguPublishPage

async def upload_song(song_path: str):
    path = Path(song_path)
    title = path.stem
    print(f"Uploading: {title} from {path}")
    
    config = BrowserConfig(headless=True)
    browser = PlaywrightBrowser(config)
    await browser.launch()
    
    account_repo = JsonAccountRepository(Path("config/accounts.json"))
    accounts = account_repo.get_all()
    account = next((a for a in accounts if a.email == "tgobox.jkt.1747@gmail.com"), None)
    
    payload = UploadPayload(
        track_path=path,
        title=title,
        artist="Kurs",
        genre="Pop",
        songwriter_name="Kusriyah"
    )
    
    page = await browser.new_page()
    login_page = LoginPage(page)
    print("Logging in...")
    await login_page.login(account.email, account.password)

    publish_page = LaguPublishPage(page)
    print("Navigating to publish page...")
    await publish_page.go_to_single_publish()
    print("Filling track information...")
    await publish_page.fill_track_information(payload)
    print("Filling release settings...")
    await publish_page.fill_release_settings(payload)
    print("Skipping more options...")
    await publish_page.skip_more_options()
    
    print("Submitting to drafts...")
    await publish_page.submit()
    
    print("Done!")
    await browser.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python auto_upload.py <dir_with_wavs>")
        sys.exit(1)
        
    dir_path = Path(sys.argv[1])
    if not dir_path.is_dir():
        # Fallback for single file
        asyncio.run(upload_song(str(dir_path)))
    else:
        wavs = sorted(list(dir_path.glob("*.wav")))
        print(f"Found {len(wavs)} wav files.")
        for w in wavs:
            print(f"--- Processing {w.name} ---")
            try:
                asyncio.run(upload_song(str(w)))
            except Exception as e:
                print(f"FAILED on {w.name}: {e}")
            print("--- Done with song ---")

