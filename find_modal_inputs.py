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
    
    # Find inputs inside .so-form-modal
    modal_inputs = await page._page.evaluate('''() => {
        const modal = document.querySelector(".so-form-modal");
        if (!modal) return "Modal not found";
        
        const inputs = [...modal.querySelectorAll("input, button, select, div, span, label")];
        return inputs.map(el => ({
            tag: el.tagName,
            type: el.type || "",
            className: el.className || "",
            id: el.id || "",
            innerText: el.innerText || "",
            placeholder: el.placeholder || "",
            value: el.value || ""
        })).filter(x => x.tag === "INPUT" || x.tag === "BUTTON" || x.className.includes("select") || x.className.includes("input"));
    }''')
    
    print("Modal elements details:")
    for idx, el in enumerate(modal_inputs):
        print(f"[{idx}] Tag: {el['tag']} | Type: {el['type']} | Class: {el['className']} | ID: {el['id']} | Value: {el['value']} | Placeholder: {el['placeholder']} | Text: '{el['innerText']}'")
        
    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
