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
    
    print("Opening Frozen Pitchers Test draft...")
    await page.evaluate('''() => {
        const rows = [...document.querySelectorAll('tr')];
        const row = rows.find(r => r.innerText.includes('Frozen Pitchers Test'));
        if (row) {
            const buttons = [...row.querySelectorAll('button')];
            if (buttons.length > 0) buttons[0].click();
        }
    }''')
    await asyncio.sleep(8)
    
    # Function to dismiss modals
    async def dismiss():
        await page.evaluate('''() => {
            document.querySelectorAll(".semi-modal-close, .semi-modal-close-button").forEach(btn => btn.click());
            const btns = [...document.querySelectorAll("button, span, div")];
            const closeWords = ['nanti saja', 'not now', 'tutup', 'got it'];
            btns.forEach(btn => {
                if (btn.innerText && closeWords.includes(btn.innerText.trim().toLowerCase())) {
                    btn.click();
                }
            });
        }''')
        await asyncio.sleep(1)
        
    await dismiss()
    
    # Loop to click Selanjutnya until we reach step 4
    for step in range(1, 4):
        print(f"Step {step}: Clicking Selanjutnya...")
        await page.evaluate('''() => {
            const btns = [...document.querySelectorAll('button, div, span, a')];
            const btn = btns.find(b => b.innerText && (b.innerText.trim() === 'Next' || b.innerText.trim() === 'Selanjutnya') && b.getBoundingClientRect().width > 0);
            if (btn) btn.click();
        }''')
        await asyncio.sleep(3)
        # Dismiss any validation dialog
        await page.evaluate('''() => {
            const modal = document.querySelector('.semi-modal');
            if (modal) {
                const btns = [...modal.querySelectorAll('button, span, div')];
                const nantiBtn = btns.find(b => b.innerText && (b.innerText.trim() === 'Nanti' || b.innerText.trim() === 'Later'));
                if (nantiBtn) nantiBtn.click();
            }
        }''')
        await asyncio.sleep(2)
        await dismiss()
        
    # We are on Step 4 (Peninjauan)
    print("Dumping validation errors on review page...")
    info = await page.evaluate('''() => {
        const text = document.body.innerText;
        
        // Find all red error text elements or validation labels on the page
        const errorElements = [];
        const all = document.querySelectorAll('*');
        for (const el of all) {
            const style = window.getComputedStyle(el);
            const color = style.color;
            if ((color.includes('255, 77, 79') || color.includes('255, 0, 0') || color.includes('red')) && el.innerText && el.innerText.trim().length > 0) {
                if (el.getBoundingClientRect().width > 0) {
                    // Try to get unique text
                    const txt = el.innerText.trim();
                    if (!errorElements.includes(txt)) {
                        errorElements.push(txt);
                    }
                }
            }
        }
        return {
            text: text,
            errors: errorElements
        };
    }''')
    
    print("--- Red error messages ---")
    for err in info["errors"]:
        print("-", err)
    print("--------------------------")
    
    # Screenshot of step 4 review details
    await page.screenshot(path="review_errors_scrolled.png", full_page=True)
    print("Saved review_errors_scrolled.png")
    
    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
