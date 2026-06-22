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
    
    # Open Frozen Pitchers Test 2
    await page.evaluate('''() => {
        const rows = [...document.querySelectorAll('tr')];
        const row = rows.find(r => r.innerText.includes('Frozen Pitchers Test 2'));
        if (row) {
            const buttons = [...row.querySelectorAll('button')];
            if (buttons.length > 0) buttons[0].click();
        }
    }''')
    await asyncio.sleep(8)
    
    # Dismiss popups
    await page.evaluate('''() => {
        document.querySelectorAll(".semi-modal-close, .semi-modal-close-button").forEach(btn => btn.click());
    }''')
    await asyncio.sleep(1)
    
    # Check composers and lyricists text
    info = await page.evaluate('''() => {
        const composersDiv = document.getElementById("composers");
        const lyricistsDiv = document.getElementById("lyricists");
        const mainArtistsDiv = document.getElementById("mainArtists");
        
        return {
            composers: composersDiv ? composersDiv.innerText : 'not_found',
            lyricists: lyricistsDiv ? lyricistsDiv.innerText : 'not_found',
            mainArtists: mainArtistsDiv ? mainArtistsDiv.innerText : 'not_found'
        };
    }''')
    
    print("--- STEP 1 DUMP ---")
    print("Composers (Songwriter) div text:")
    print(info["composers"])
    print("\nLyricists div text:")
    print(info["lyricists"])
    print("\nMain Artists div text:")
    print(info["mainArtists"])
    print("--------------------")
    
    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
