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
    config = BrowserConfig(headless=True) # Let's keep it headless
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
    
    # We are now on the Track page.
    # The tracks are named 1, 2, 3... 10.
    track_files = sorted(glob.glob("/home/aaa/Downloads/Jane_Eyre_Songs/Fire Stone/*.wav"))
    
    for i, track_file in enumerate(track_files):
        track_num = i + 1
        track_name = os.path.splitext(os.path.basename(track_file))[0]
        print(f"DEBUG: Filling Track {track_num}: {track_name}")
        
        # Expand the track if it's not expanded
        # The track header is a div containing the number.
        header = page._page.locator(".semi-collapse-header").nth(i)
        
        # Let's take a screenshot before clicking to see
        await page._page.screenshot(path=f"debug_track_{track_num}_pre.png", full_page=True)
        
        # Ensure it's expanded by clicking it
        await header.click(force=True)
        await asyncio.sleep(2)
        
        # Take a screenshot to see the expanded fields
        await page._page.screenshot(path=f"debug_track_{track_num}_expanded.png", full_page=True)
        
        # Find the inputs within this track's panel!
        panel = page._page.locator(".semi-collapse-panel").nth(i)
        
        # 1. Judul
        title_input = panel.locator("input[type='text']").first
        await title_input.fill("")
        await title_input.type(track_name, delay=50)
        await title_input.evaluate('''el => {
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
        }''')
        
        # 2. Bahasa Judul (English / Inggris)
        # It's a dropdown. Let's click the nearest semi-select
        try:
            lang_dropdown = panel.locator(".semi-select").first
            await lang_dropdown.click(force=True)
            await asyncio.sleep(1)
            # The options pop up in the body, not in the panel!
            await page._page.locator("[class*='option'], [class*='select-option']").filter(has_text="English").first.click(force=True)
        except Exception as e:
            print("Language fill failed:", e)
            
        # We'll just break after 1 to inspect the screenshots
        break
        
    await browser.close()

asyncio.run(main())
