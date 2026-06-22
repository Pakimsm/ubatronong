import asyncio
from pathlib import Path
from src.core.browser import PlaywrightBrowser
from src.core.account_manager import JsonAccountRepository
from src.models.browser_config import BrowserConfig
from src.pages.login import LoginPage
from src.pages.lagu_publish import LaguPublishPage

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
    
    # Click "tambah" button for mainArtists
    print("Clicking tambah button for mainArtists...")
    await page._page.evaluate('''() => {
        const mainArtistsDiv = document.getElementById("mainArtists");
        if (mainArtistsDiv) {
            const btn = mainArtistsDiv.querySelector("button");
            if (btn) btn.click();
        }
    }''')
    await asyncio.sleep(2)
    
    # Select artist
    await page.click("#artistProfile")
    await asyncio.sleep(1)
    await page._page.evaluate('''() => {
        const container = document.getElementById("artistProfile");
        if (!container) return;
        const input = container.querySelector("input");
        if (input) {
            input.focus();
            const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value").set;
            setter.call(input, "Kurs");
            input.dispatchEvent(new Event("input", {bubbles: true}));
            input.dispatchEvent(new Event("change", {bubbles: true}));
        }
    }''')
    await asyncio.sleep(2)
    await page._page.evaluate('''() => {
        const options = [...document.querySelectorAll("[class*='target-option']")];
        if (options.length > 0) options[0].click();
    }''')
    await asyncio.sleep(1)
    await page._page.evaluate('''() => {
        const modal = document.querySelector(".so-form-modal");
        if (!modal) return;
        const buttons = [...modal.querySelectorAll("button")];
        const kirim = buttons.find(b => b.innerText && /kirim|submit|simpan|save/i.test(b.innerText));
        if (kirim) kirim.click();
    }''')
    await asyncio.sleep(2)
    
    print("URL after artist select:", await page.current_url())
    
    # Wait for potential redirect
    await asyncio.sleep(5)
    url = await page.current_url()
    print("URL after 5 seconds:", url)
    
    if "vas-quota" in url:
        print("Redirected to vas-quota! Trying to navigate back to publish/single...")
        await page.goto("https://www.soundon.global/library/publish/single?lang=id&region=ID")
        await asyncio.sleep(5)
        print("URL after navigating back:", await page.current_url())
        await page.screenshot(path="debug_after_nav_back.png", full_page=True)
        print("Saved debug_after_nav_back.png")
        
    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
