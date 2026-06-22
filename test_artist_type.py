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
    
    # Wait for page load
    print("Waiting for page load...")
    await asyncio.sleep(5)
    
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
    
    # Click #artistProfile select
    print("Clicking #artistProfile select...")
    await page.click("#artistProfile")
    await asyncio.sleep(1)
    
    # Dump inputs inside #artistProfile after click
    inputs = await page._page.evaluate('''() => {
        const container = document.getElementById("artistProfile");
        if (!container) return "Container not found";
        const inps = [...container.querySelectorAll("input")];
        return inps.map(i => ({
            tag: i.tagName,
            type: i.type,
            className: i.className,
            value: i.value
        }));
    }''')
    print("Inputs inside #artistProfile after click:", inputs)
    
    # Let's type 'Kurs' using Playwright or JS
    print("Typing 'Kurs'...")
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
    
    # Take screenshot of options dropdown
    await page._page.screenshot(path="debug_artist_modal_live.png", full_page=True)
    print("Saved debug_artist_modal_live.png")
    
    # Dump visible options in the body
    opts = await page._page.evaluate('''() => {
        const options = [...document.querySelectorAll(".semi-select-option, [class*='option'], [role='option']")];
        return options.map(o => ({
            text: o.innerText,
            className: o.className
        }));
    }''')
    print("Options in DOM:", opts)
    
    # Click match
    await page._page.evaluate('''() => {
        const options = [...document.querySelectorAll(".semi-select-option, [class*='option'], [role='option']")];
        const match = options.find(o => o.innerText && o.innerText.toLowerCase().includes("kurs"));
        if (match) {
            match.click();
        } else if (options.length > 0) {
            options[0].click();
        }
    }''')
    await asyncio.sleep(1)
    
    # Click 'Kirim'
    print("Clicking 'Kirim' button...")
    await page._page.evaluate('''() => {
        const modal = document.querySelector(".so-form-modal");
        if (!modal) return;
        const buttons = [...modal.querySelectorAll("button")];
        const kirim = buttons.find(b => b.innerText && /kirim|submit|simpan|save/i.test(b.innerText));
        if (kirim) kirim.click();
    }''')
    await asyncio.sleep(2)
    
    # Check if artist is added
    added = await page._page.evaluate('''() => {
        const mainArtistsDiv = document.getElementById("mainArtists");
        return mainArtistsDiv ? mainArtistsDiv.innerText : "Not found";
    }''')
    print("mainArtists after submit:", added)
    
    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
