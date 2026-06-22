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
    
    # Find any element containing "Tambahkan artis utama" and print its path/attrs
    matches = await page._page.evaluate('''() => {
        const elements = [...document.querySelectorAll("*")];
        const matching = [];
        for (let el of elements) {
            if (el.childNodes.length > 0) {
                // Check direct text nodes
                for (let child of el.childNodes) {
                    if (child.nodeType === Node.TEXT_NODE && child.nodeValue.includes("Tambahkan artis utama")) {
                        // Traverse up and get path
                        let path = [];
                        let curr = el;
                        while (curr) {
                            path.push(curr.tagName + (curr.className ? "." + curr.className.split(" ").join(".") : "") + (curr.id ? "#" + curr.id : ""));
                            curr = curr.parentElement;
                        }
                        matching.push({
                            tag: el.tagName,
                            className: el.className,
                            id: el.id,
                            path: path.reverse().join(" > "),
                            innerHTML: el.innerHTML.substring(0, 500)
                        });
                        break;
                    }
                }
            }
        }
        return matching;
    }''')
    
    print(f"Found {len(matches)} elements containing the target text:")
    for idx, m in enumerate(matches):
        print(f"Match {idx+1}:")
        print(f"  Path: {m['path']}")
        print(f"  Tag: {m['tag']} | Class: {m['className']} | ID: {m['id']}")
        print(f"  HTML: {m['innerHTML']}")
        print("-" * 50)
        
    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
