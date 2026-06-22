import asyncio
from pathlib import Path
from src.core.browser import PlaywrightBrowser
from src.core.account_manager import JsonAccountRepository
from src.models.browser_config import BrowserConfig
from src.pages.album_publish import AlbumPublishPage
from src.models.upload_payload import UploadPayload
from src.pages.login import LoginPage

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
    
    payload = UploadPayload(
        track_path=Path("/home/aaa/Downloads/Jane_Eyre_Songs/Fire Stone"),
        cover_path=Path("/home/aaa/.gemini/antigravity-cli/brain/1dbfe5da-4ecd-4f07-8245-73d55f0fbb7d/cover_art_1781667614560.jpg"),
        title="Fire Stone",
        title_language="English",
        genre="Country",
        artist="Kurs",
        release_date=""
    )
    
    publish_page = AlbumPublishPage(page)
    draft_url = "https://www.soundon.global/library/publish/album?source=draft&id=7652210850094319632&lang=id"
    print(f"Navigating to {draft_url}")
    await publish_page.go_to_album_publish(url=draft_url)
    
    print("Filling album information...")
    await publish_page.fill_album_information(payload)
    
    print("Going to next page...")
    import re
    # Hit "Selanjutnya" to save info
    await page._page.locator("button, a").filter(has_text=re.compile(r"^Selanjutnya$|^Next$", re.IGNORECASE)).last.click(force=True)
    await asyncio.sleep(8)
    
    print("Saving to draft...")
    await page.evaluate('''() => {
        const btns = [...document.querySelectorAll('button')];
        const saveBtn = btns.find(b => b.innerText && (b.innerText.toLowerCase().includes('save to draft') || b.innerText.toLowerCase().includes('simpan ke draf')));
        if(saveBtn) saveBtn.click();
    }''')
    await asyncio.sleep(5)
    
    print("Taking final screenshot of drafts...")
    await page._page.goto("https://www.soundon.global/library/list?lang=id&type=drafts", wait_until="networkidle")
    await asyncio.sleep(5)
    await page._page.screenshot(path="user_draft_fixed.png", full_page=True)
    
    await browser.close()

asyncio.run(main())
