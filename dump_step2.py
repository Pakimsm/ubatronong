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
    
    print("Clicking edit button...")
    await page.evaluate('''() => {
        const rows = [...document.querySelectorAll('tr')];
        const row = rows.find(r => r.innerText.includes('Fire In The Bed Task Test'));
        if (row) {
            const buttons = [...row.querySelectorAll('button')];
            if (buttons.length > 0) buttons[0].click();
        }
    }''')
    await asyncio.sleep(8)
    
    # Dismiss any popups
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
    await asyncio.sleep(2)
    
    print("Clicking Selanjutnya to go to Step 2...")
    await page.evaluate('''() => {
        const btns = [...document.querySelectorAll('button, div, span, a')];
        const btn = btns.find(b => b.innerText && (b.innerText.trim() === 'Next' || b.innerText.trim() === 'Selanjutnya') && b.getBoundingClientRect().width > 0);
        if (btn) btn.click();
    }''')
    await asyncio.sleep(5)
    
    # Dismiss any validation error modal
    await page.evaluate('''() => {
        const modal = document.querySelector('.semi-modal');
        if (modal) {
            const btns = [...modal.querySelectorAll('button, span, div')];
            const nantiBtn = btns.find(b => b.innerText && (b.innerText.trim() === 'Nanti' || b.innerText.trim() === 'Later'));
            if (nantiBtn) nantiBtn.click();
        }
    }''')
    await asyncio.sleep(3)
    
    # Take screenshot of Step 2
    await page.screenshot(path="draft_step2.png", full_page=True)
    print("Saved draft_step2.png")
    
    # Dump inputs and text elements on Step 2
    info = await page.evaluate('''() => {
        const labels = [...document.querySelectorAll('div, span, label, p')].map(el => el.innerText).filter(Boolean);
        const inputs = [...document.querySelectorAll('input')].map(i => ({
            name: i.name,
            type: i.type,
            value: i.value,
            placeholder: i.placeholder,
            checked: i.checked,
            id: i.id
        }));
        return {
            text: document.body.innerText.substring(0, 3000),
            inputs: inputs
        };
    }''')
    
    print("--- Step 2 Text Excerpt ---")
    print(info["text"])
    print("--- Step 2 Inputs ---")
    for inp in info["inputs"]:
        print(inp)
        
    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
