"""Debug: expand ONE track card and dump its inputs/selects."""
import asyncio
import json
from pathlib import Path
from src.core.browser import PlaywrightBrowser
from src.core.account_manager import JsonAccountRepository
from src.models.browser_config import BrowserConfig
from src.pages.album_publish import AlbumPublishPage
from src.pages.login import LoginPage
from src.models.upload_payload import UploadPayload
import glob

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
    await album_page.fill_album_information(payload)
    print("On track list page")

    audio_files = sorted(
        glob.glob(f"{payload.track_path}/*.wav") +
        glob.glob(f"{payload.track_path}/*.mp3") +
        glob.glob(f"{payload.track_path}/*.flac")
    )

    # Upload first file only
    async with page._page.expect_file_chooser(timeout=15000) as fc_info:
        await page._page.locator("*:has-text('Tambah Lagu')").last.click(force=True)
    fc = await fc_info.value
    await fc.set_files(audio_files[0])
    await asyncio.sleep(5)

    # Check if track card is already open (details[open]) or closed
    card_state = await page._page.evaluate('''() => {
        const cards = [...document.querySelectorAll("details.card-oymaL6")];
        return cards.map(c => ({
            open: c.open,
            class: c.className,
            summary_text: c.querySelector("summary")?.innerText?.trim().substring(0,80)
        }));
    }''')
    print("Track cards:", json.dumps(card_state, indent=2))

    # Click the first card's summary to expand if not already open
    first_card = page._page.locator("details.card-oymaL6").first
    first_summary = page._page.locator("details.card-oymaL6 > summary.preview-Z6ovek").first
    is_open = await page._page.evaluate("() => document.querySelector('details.card-oymaL6')?.open")
    print(f"First card open: {is_open}")

    if not is_open:
        await first_summary.click(force=True)
        await asyncio.sleep(1)

    # Dump content of first card
    card_content = await page._page.evaluate('''() => {
        const card = document.querySelector("details.card-oymaL6");
        if (!card) return "no card";
        const inputs = [...card.querySelectorAll("input")].map(el => ({
            id: el.id, type: el.type, placeholder: el.placeholder, value: el.value.substring(0,30), class: el.className.substring(0,60), name: el.name
        }));
        const selects = [...card.querySelectorAll("[role='combobox']")].map(el => ({
            id: el.id, class: el.className.substring(0,80), text: el.innerText?.trim().substring(0,50), expanded: el.getAttribute("aria-expanded")
        }));
        const labels = [...card.querySelectorAll("label, .so-label p, [class*='label']")].map(el => el.innerText?.trim()).filter(Boolean).slice(0,20);
        const buttons = [...card.querySelectorAll("button")].map(b => b.innerText?.trim()).filter(Boolean).slice(0,10);
        const html = card.innerHTML.substring(0, 4000);
        return {inputs, selects, labels, buttons, html};
    }''')
    with open("debug_track_card.html", "w") as f:
        f.write(card_content.get("html", ""))
    print("Card inputs:", json.dumps(card_content["inputs"], indent=2))
    print("Card selects:", json.dumps(card_content["selects"], indent=2))
    print("Card labels:", card_content["labels"])
    print("Card buttons:", card_content["buttons"])

    await page._page.screenshot(path="debug_track_open.png", full_page=True)
    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
