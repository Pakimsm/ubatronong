import asyncio
from pathlib import Path
from src.core.browser import PlaywrightBrowser
from src.core.account_manager import JsonAccountRepository
from src.models.browser_config import BrowserConfig
from src.pages.album_publish import AlbumPublishPage
from src.pages.login import LoginPage
import json
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
    track_names = [os.path.splitext(os.path.basename(t))[0] for t in track_files]
    
    # We will inject a JS function to fill the tracks
    result = await page._page.evaluate('''([trackNames]) => {
        return new Promise((resolve) => {
            // Find all track headers "1", "2"...
            let headers = [...document.querySelectorAll('div')].filter(d => d.innerText && d.innerText.match(/^[0-9]+$/) && d.nextElementSibling);
            if (headers.length === 0) {
                // SoundOn might render them as list items
                let lis = [...document.querySelectorAll('li')];
                headers = lis.filter(li => {
                    let firstText = (li.innerText || '').trim().split('\\n')[0];
                    return firstText.match(/^[0-9]+$/);
                });
            }
            
            if(headers.length === 0) resolve("ERROR: No track headers found.");
            
            // Just return how many we found and their HTML snippets for debugging
            resolve("Found " + headers.length + " track containers.");
        });
    }''', [track_names])
    
    print(result)
    
    await browser.close()

asyncio.run(main())
