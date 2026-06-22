"""Full end-to-end test: album info + track upload + verify."""
import asyncio
import json
from pathlib import Path
from src.core.browser import PlaywrightBrowser
from src.core.account_manager import JsonAccountRepository
from src.models.browser_config import BrowserConfig
from src.pages.album_publish import AlbumPublishPage
from src.pages.login import LoginPage
from src.models.upload_payload import UploadPayload

async def main():
    config = BrowserConfig(headless=True, default_timeout=60_000)
    browser = PlaywrightBrowser(config)
    account_repo = JsonAccountRepository(Path("config/accounts.json"))
    accounts = account_repo.get_active()
    account = next((a for a in accounts if "tgobox" in a.email), accounts[0])
    await browser.launch()
    page = await browser.new_page()

    login = LoginPage(page)
    await login.login(account.email, account.password)
    await asyncio.sleep(3)

    payload = UploadPayload(
        title="Fire Stone",
        artist="Kurs",
        genre="Pop",
        release_date="2025-01-01",
        track_path=Path("/home/aaa/Downloads/Jane_Eyre_Songs/Fire Stone"),
        cover_path=Path("/home/aaa/Downloads/Jane_Eyre_Songs/madwoman.png"),
    )

    album_page = AlbumPublishPage(page)
    await album_page.go_to_album_publish()

    print("=== fill_album_information ===")
    await album_page.fill_album_information(payload)
    print("Album info OK")

    print("=== upload_tracks ===")
    await album_page.upload_tracks(payload)
    print("upload_tracks returned")

    # Wait for JS metadata fill to settle
    await asyncio.sleep(5)
    await page._page.screenshot(path="debug_after_tracks.png", full_page=True)

    # Check track state
    track_state = await page._page.evaluate('''() => {
        const url = location.href;
        const inputs = [...document.querySelectorAll("input[type='text']")].map(el => ({
            id: el.id, value: el.value, placeholder: el.placeholder, class: el.className.substring(0,50)
        })).filter(el => el.value || el.placeholder);
        const panels = [...document.querySelectorAll(".semi-collapse-panel")];
        return {
            url,
            page_text_sample: document.body.innerText.substring(0, 300),
            input_count: inputs.length,
            inputs_with_values: inputs.filter(i => i.value).slice(0,10),
            panels_count: panels.length,
        };
    }''')
    print("Track page state:", json.dumps(track_state, indent=2))

    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
