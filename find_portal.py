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
    
    # Search the entire DOM for "Tambahkan artis utama"
    portal_info = await page._page.evaluate('''() => {
        const allElements = [...document.querySelectorAll("*")];
        const match = allElements.find(el => el.innerText && el.innerText.includes("Tambahkan artis utama") && el.children.length > 0 && !el.innerText.includes("Detail lagu"));
        if (!match) return "Not found";
        
        return {
            tagName: match.tagName,
            className: match.className,
            id: match.id,
            innerHTML: match.innerHTML.substring(0, 1000) // first 1000 chars of HTML
        };
    }''')
    print("Portal element info:", portal_info)
    
    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
