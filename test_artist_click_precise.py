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
    
    # Let's type 'Kurs'
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
    
    # Find all elements matching option and dump their details
    opt_details = await page._page.evaluate('''() => {
        const elements = [...document.querySelectorAll("*")].filter(el => el.className && typeof el.className === "string" && (el.className.includes("option") || el.className.includes("select-option")));
        return elements.map(el => ({
            tag: el.tagName,
            className: el.className,
            innerText: el.innerText,
            attributes: [...el.attributes].map(a => ({ name: a.name, value: a.value }))
        }));
    }''')
    
    print("Detailed option elements:")
    for idx, o in enumerate(opt_details):
        print(f"[{idx}] Tag: {o['tag']} | Class: {o['className']} | Text: '{o['innerText']}' | Attributes: {o['attributes']}")
        
    # Let's try clicking specifically the target-option-vGQKoC class element
    print("Clicking precisely on the option with class target-option...")
    await page._page.evaluate('''() => {
        const option = document.querySelector("[class*='target-option']");
        if (option) {
            option.click();
            console.log("Clicked target-option:", option.className);
        } else {
            console.log("target-option not found");
        }
    }''')
    await asyncio.sleep(1)
    
    # Check screen after click
    await page._page.screenshot(path="debug_after_precise_click.png", full_page=True)
    print("Saved debug_after_precise_click.png")
    
    # Click 'Kirim'
    print("Clicking 'Kirim'...")
    await page._page.evaluate('''() => {
        const modal = document.querySelector(".so-form-modal");
        if (!modal) return;
        const buttons = [...modal.querySelectorAll("button")];
        const kirim = buttons.find(b => b.innerText && /kirim|submit|simpan|save/i.test(b.innerText));
        if (kirim) kirim.click();
    }''')
    await asyncio.sleep(2)
    
    # Verify mainArtists HTML content
    added = await page._page.evaluate('''() => {
        const mainArtistsDiv = document.getElementById("mainArtists");
        return mainArtistsDiv ? mainArtistsDiv.innerHTML : "Not found";
    }''')
    print("mainArtists HTML after precise submit:", added[:1000])
    
    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
