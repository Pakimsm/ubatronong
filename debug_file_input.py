import asyncio
from pathlib import Path
from src.core.browser import PlaywrightBrowser
from src.core.account_manager import JsonAccountRepository
from src.models.browser_config import BrowserConfig
from src.pages.album_publish import AlbumPublishPage
from src.pages.login import LoginPage

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
    
    # Expand the first track
    await page._page.evaluate('''() => {
        let divs = [...document.querySelectorAll('div')].filter(d => d.innerText && d.innerText.match(/^[0-9]+$/));
        if(divs.length > 0) divs[0].click();
    }''')
    await asyncio.sleep(2)
    
    res = await page._page.evaluate('''() => {
        let inps = document.querySelectorAll('input[type="file"]');
        return {
            count: inps.length,
            classes: [...inps].map(i => i.className),
            parents: [...inps].map(i => i.parentElement.className)
        }
    }''')
    print("File inputs found:", res)
    await browser.close()

asyncio.run(main())
