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
    print("Logging in...")
    await login_page.login(account.email, account.password)
    
    print("Navigating to drafts page...")
    await page.goto("https://www.soundon.global/library/list?lang=id&type=drafts")
    await asyncio.sleep(5)
    
    print("Clicking edit button for 'Frozen Pitchers Test'...")
    click_res = await page.evaluate('''() => {
        const rows = [...document.querySelectorAll('tr')];
        const row = rows.find(r => r.innerText.includes('Frozen Pitchers Test'));
        if (row) {
            const buttons = [...row.querySelectorAll('button')];
            if (buttons.length > 0) {
                buttons[0].click();
                return 'clicked_edit_button';
            }
        }
        return 'row_not_found';
    }''')
    print("Click result:", click_res)
    await asyncio.sleep(12)
    
    # Save screenshot of draft editor page
    await page.screenshot(path="frozen_pitchers_inspect.png", full_page=True)
    print("Saved frozen_pitchers_inspect.png")
    
    # Dump page text and validation error messages
    info = await page.evaluate('''() => {
        // Collect page text
        const text = document.body.innerText;
        
        // Find visible error messages
        const errors = [...document.querySelectorAll('.semi-form-field-error-message, .error-message')].map(el => el.innerText);
        
        // Let's check which elements have the red error icon or similar in Step 1
        return {
            url: window.location.href,
            errors: errors
        };
    }''')
    
    print("Draft URL:", info["url"])
    print("--- Errors on Page ---")
    print(info["errors"])
    
    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
