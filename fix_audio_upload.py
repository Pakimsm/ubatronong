import asyncio
from pathlib import Path
from src.core.browser import PlaywrightBrowser
from src.core.account_manager import JsonAccountRepository
from src.models.browser_config import BrowserConfig
from src.pages.album_publish import AlbumPublishPage
from src.pages.login import LoginPage
import os
import glob

async def main():
    config = BrowserConfig(headless=True)
    browser = PlaywrightBrowser(config)
    await browser.launch()
    page = await browser.new_page()
    
    account_repo = JsonAccountRepository(Path("config/accounts.json"))
    target_account = next(a for a in account_repo.get_all() if a.email == "tgobox.jkt.1747@gmail.com")
    
    login_page = LoginPage(page)
    await login_page.login(target_account.email, target_account.password)
    
    draft_url = "https://www.soundon.global/library/publish/album?source=draft&id=7652210850094319632&lang=id"
    await page._page.goto(draft_url, wait_until="networkidle")
    await asyncio.sleep(5)
    
    publish_page = AlbumPublishPage(page)
    try:
        popup_sel = "button:has-text('Nanti saja'), button:has-text('Not now'), .semi-modal-close, button:has-text('Tutup'), button:has-text('Got it')"
        await publish_page.wait_for_element(popup_sel, timeout=6000)
        await publish_page.page.click(popup_sel, force=True)
        await asyncio.sleep(1)
    except Exception:
        pass
        
    await page._page.locator("button, a").filter(has_text="Selanjutnya").last.click(force=True)
    await asyncio.sleep(8)
    
    track_files = sorted(glob.glob("/home/aaa/Downloads/Jane_Eyre_Songs/Fire Stone/*.wav"))
    
    for i, track_file in enumerate(track_files):
        track_num = i + 1
        track_name = os.path.splitext(os.path.basename(track_file))[0]
        print(f"DEBUG: Uploading Audio for Track {track_num}: {track_name}")
        
        try:
            # The 11 file inputs with class 'semi-upload-hidden-input' map to:
            # index 0: Album Cover
            # index 1-10: Track 1 to 10 audio uploads
            global_input = page._page.locator(".semi-upload-hidden-input").nth(track_num)
            
            # DIRECTLY attach the file!
            await global_input.set_input_files(track_file)
            print(f"File {track_name} attached directly to hidden input {track_num}. Waiting 15s for upload to process...")
            await asyncio.sleep(15)
        except Exception as e:
            print(f"Error uploading {track_name}:", e)
        
    print("Saving to draft...")
    await page._page.evaluate('''() => {
        const btns = [...document.querySelectorAll('button')];
        const saveBtn = btns.find(b => b.innerText && (b.innerText.toLowerCase().includes('save to draft') || b.innerText.toLowerCase().includes('simpan ke draf')));
        if(saveBtn) saveBtn.click();
    }''')
    await asyncio.sleep(5)
    await browser.close()

asyncio.run(main())
