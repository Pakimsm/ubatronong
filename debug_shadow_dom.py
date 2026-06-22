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
    
    # Let's inspect the entire DOM structure around dialog using deep check
    dom_info = await page._page.evaluate('''() => {
        const dialog = document.querySelector("dialog");
        if (!dialog) return "No dialog element found";
        
        let hasShadow = !!dialog.shadowRoot;
        let innerHTML = dialog.innerHTML;
        let childrenCount = dialog.children.length;
        
        // Let's recursively find if there is a shadow root or any nested element
        function getInfo(el) {
            let res = {
                tag: el.tagName,
                className: el.className,
                hasShadow: !!el.shadowRoot,
                children: []
            };
            
            // Check light DOM children
            for (let child of el.children) {
                res.children.push(getInfo(child));
            }
            
            // Check shadow DOM children
            if (el.shadowRoot) {
                res.shadowRootChildren = [];
                for (let child of el.shadowRoot.children) {
                    res.shadowRootChildren.push(getInfo(child));
                }
            }
            return res;
        }
        
        return {
            hasShadow,
            childrenCount,
            innerHTML,
            tree: getInfo(dialog)
        };
    }''')
    print("Dialog DOM info:", dom_info)
    
    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
