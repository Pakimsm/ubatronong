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
    await asyncio.sleep(3)
    
    # Let's find inputs inside the modal
    inputs_info = await page._page.evaluate('''() => {
        const modal = document.querySelector("dialog, .semi-modal, .so-form-modal-dialog");
        if (!modal) return "Modal not found";
        
        const inputs = [...modal.querySelectorAll("input, select, textarea, button")];
        return inputs.map(inp => ({
            tag: inp.tagName,
            type: inp.type,
            placeholder: inp.placeholder,
            value: inp.value,
            id: inp.id,
            className: inp.className,
            innerText: inp.innerText
        }));
    }''')
    print("Modal elements:", inputs_info)
    
    # Type into the select/input of the modal
    print("Typing 'Kurs' into modal input...")
    await page._page.evaluate('''() => {
        const modal = document.querySelector("dialog, .semi-modal, .so-form-modal-dialog");
        if (!modal) return;
        const input = modal.querySelector("input[type='text'], input");
        if (input) {
            input.focus();
            const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value").set;
            setter.call(input, "Kurs");
            input.dispatchEvent(new Event("input", {bubbles: true}));
            input.dispatchEvent(new Event("change", {bubbles: true}));
        }
    }''')
    await asyncio.sleep(2)
    
    await page._page.screenshot(path="debug_artist_after_type.png", full_page=True)
    print("Saved debug_artist_after_type.png")
    
    # Let's see if options appear in a listbox/dropdown
    opts_info = await page._page.evaluate('''() => {
        const options = [...document.querySelectorAll(".semi-select-option, [class*='option'], [role='option']")];
        return options.map(opt => ({
            text: opt.innerText,
            className: opt.className
        }));
    }''')
    print("Dropdown options found:", opts_info)
    
    # Click the matching option
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
    
    await page._page.screenshot(path="debug_after_option_click.png", full_page=True)
    print("Saved debug_after_option_click.png")
    
    # Click submit/kirim button in the modal
    print("Clicking submit/kirim...")
    await page._page.evaluate('''() => {
        const modal = document.querySelector("dialog, .semi-modal, .so-form-modal-dialog");
        if (!modal) return;
        const buttons = [...modal.querySelectorAll("button")];
        const kirim = buttons.find(b => b.innerText && /kirim|submit|simpan|save/i.test(b.innerText));
        if (kirim) kirim.click();
    }''')
    await asyncio.sleep(2)
    
    await page._page.screenshot(path="debug_after_kirim.png", full_page=True)
    print("Saved debug_after_kirim.png")
    
    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
