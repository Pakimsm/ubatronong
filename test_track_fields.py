import asyncio
from pathlib import Path
from src.core.browser import PlaywrightBrowser
from src.core.account_manager import JsonAccountRepository
from src.models.browser_config import BrowserConfig
from src.pages.album_publish import AlbumPublishPage
from src.pages.login import LoginPage
import json

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
    
    # Extract structural info of visible inputs
    fields = await page._page.evaluate('''() => {
        let results = [];
        let labels = document.querySelectorAll('label, .semi-form-field-label');
        labels.forEach(l => {
            let text = l.innerText.trim();
            if(!text) return;
            // find nearest input or button
            let parent = l.parentElement;
            let input = null;
            while(parent && parent.tagName !== 'BODY') {
                input = parent.querySelector('input, textarea, button, .semi-select');
                if(input) break;
                parent = parent.parentElement;
            }
            results.push({ label: text, type: input ? input.tagName + (input.type ? '[' + input.type + ']' : '') : 'none', className: input ? input.className : '' });
        });
        return results;
    }''')
    
    print(json.dumps(fields, indent=2))
    
    await browser.close()

asyncio.run(main())
