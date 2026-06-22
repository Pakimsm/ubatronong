import asyncio
from pathlib import Path
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
    await login_page.login(account.email, account.password)
    
    await page.goto("https://www.soundon.global/library/list?lang=id&type=drafts")
    await asyncio.sleep(5)
    
    # Open draft
    await page.evaluate('''() => {
        const rows = [...document.querySelectorAll('tr')];
        const row = rows.find(r => r.innerText.includes('Frozen Pitchers Test 2'));
        if (row) {
            const buttons = [...row.querySelectorAll('button')];
            if (buttons.length > 0) buttons[0].click();
        }
    }''')
    await asyncio.sleep(8)
    
    # Dismiss any popups
    await page.evaluate('''() => {
        document.querySelectorAll(".semi-modal-close, .semi-modal-close-button").forEach(btn => btn.click());
    }''')
    await asyncio.sleep(1)
    
    # Click Songwriter tambah
    print("Clicking Songwriter tambah button...")
    await page.evaluate('''() => {
        const div = document.getElementById("composers");
        if (div) {
            const btn = div.querySelector("button");
            if (btn) {
                btn.click();
                console.log("Clicked composers tambah button.");
            } else {
                console.log("Composers tambah button NOT found!");
            }
        } else {
            console.log("Composers div NOT found!");
        }
    }''')
    await asyncio.sleep(4)
    
    # Save screenshot of modal state
    await page.screenshot(path="composer_modal_debug.png", full_page=True)
    print("Saved composer_modal_debug.png")
    
    # Dump dialog/modal details
    modal_info = await page.evaluate('''() => {
        const modals = [...document.querySelectorAll('dialog, [class*="modal"], [class*="dialog"], [role="dialog"]')];
        return modals.map(m => ({
            tagName: m.tagName,
            className: m.className,
            innerText: m.innerText,
            rect: m.getBoundingClientRect(),
            inputs: [...m.querySelectorAll('input')].map(i => ({
                type: i.type,
                className: i.className,
                placeholder: i.placeholder,
                value: i.value
            }))
        }));
    }''')
    
    print("\n--- MODALS FOUND ---")
    for m in modal_info:
        print(f"Tag: {m['tagName']} | Class: {m['className']} | Visible: {m['rect']['width'] > 0}")
        print("Text:", m["innerText"])
        print("Inputs:", m["inputs"])
        print("--------------------")
        
    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
