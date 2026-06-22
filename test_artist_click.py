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
    
    # Wait for the mainArtists section to be visible
    print("Waiting for page load...")
    await asyncio.sleep(5)
    
    # Let's take a screenshot before clicking
    await page._page.screenshot(path="debug_artis_utama.png", full_page=True)
    print("Saved debug_artis_utama.png")
    
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
    
    # Take screenshot after click
    await page._page.screenshot(path="debug_artis_utama_opened.png", full_page=True)
    print("Saved debug_artis_utama_opened.png")
    
    # Dump the modal HTML
    html = await page._page.evaluate('''() => {
        const dialog = document.querySelector("dialog, .semi-modal, .so-form-modal-dialog");
        return dialog ? dialog.outerHTML : "No dialog/modal found";
    }''')
    
    with open("artis_utama_dump.html", "w") as f:
        f.write(html)
    print("Dumped artis_utama_dump.html")
    
    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
