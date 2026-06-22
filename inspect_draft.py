import asyncio
from pathlib import Path
import re
from src.core.browser import PlaywrightBrowser
from src.core.account_manager import JsonAccountRepository
from src.models.browser_config import BrowserConfig
from src.pages.login import LoginPage

async def main():
    config = BrowserConfig(headless=True)
    browser = PlaywrightBrowser(config)
    await browser.launch()
    
    account_repo = JsonAccountRepository(Path("config/accounts.json"))
    account = next(a for a in account_repo.get_all() if a.email == "tgobox.jkt.1747@gmail.com")
    
    page = await browser.new_page()
    login_page = LoginPage(page)
    print("Logging in...")
    await login_page.login(account.email, account.password)
    
    print("Navigating to drafts page...")
    await page.goto("https://www.soundon.global/library/list?type=drafts")
    await asyncio.sleep(5)
    
    # Click the first draft edit button/link
    # Let's find elements with text containing 'Edit' or the title of the draft
    print("Clicking draft...")
    edit_clicked = await page.evaluate('''() => {
        const rows = [...document.querySelectorAll('tr')];
        // Find row with 'Fire In The Bed'
        const row = rows.find(r => r.innerText.includes('Fire In The Bed'));
        if (row) {
            // Find Edit button/link or any clickable element
            const clickables = [...row.querySelectorAll('button, a, span')];
            const editBtn = clickables.find(c => c.innerText.toLowerCase().includes('edit') || c.innerText.toLowerCase().includes('lanjut') || c.innerText.toLowerCase().includes('continue'));
            if (editBtn) {
                editBtn.click();
                return 'clicked_button';
            }
            // fallback click the row/title itself
            const titleEl = row.querySelector('td') || row;
            if (titleEl) {
                titleEl.click();
                return 'clicked_title';
            }
        }
        return null;
    }''')
    
    print(f"Edit click status: {edit_clicked}")
    await asyncio.sleep(8)
    
    # Take screenshot of the draft editor
    await page.screenshot(path="draft_editor_start.png", full_page=True)
    print("Saved draft_editor_start.png")
    
    # Let's check visible errors
    errors = await page.evaluate('''() => {
        const errs = [...document.querySelectorAll('.semi-form-field-error-message, .error-message, .validation-error, .semi-modal')];
        return errs.map(el => el.innerText).filter(Boolean);
    }''')
    print("Visible validation errors:", errors)
    
    # Let's inspect fields value
    fields = await page.evaluate('''() => {
        const info = {};
        // Judul / Title
        const titleInput = document.querySelector('input[placeholder*="title"], input[placeholder*="judul"]');
        if (titleInput) info.title = titleInput.value;
        
        // Let's dump all inputs
        const inputs = [...document.querySelectorAll('input')].map(i => ({
            name: i.name,
            placeholder: i.placeholder,
            value: i.value,
            type: i.type
        }));
        info.inputs = inputs;
        return info;
    }''')
    print("Fields found:", fields)
    
    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
