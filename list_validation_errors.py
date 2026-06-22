import asyncio
from pathlib import Path
import sys

sys.path.append("/home/aaa/soundonbot")

from src.core.browser import PlaywrightBrowser
from src.core.account_manager import JsonAccountRepository
from src.models.browser_config import BrowserConfig
from src.pages.login import LoginPage
from src.pages.lagu_publish import LaguPublishPage
from src.models.upload_payload import UploadPayload

async def main():
    config = BrowserConfig(headless=True)
    browser = PlaywrightBrowser(config)
    await browser.launch()
    page = await browser.new_page()
    
    account_repo = JsonAccountRepository(Path("/home/aaa/soundonbot/config/accounts.json"))
    target_account = next(a for a in account_repo.get_all() if a.email == "tgobox.jkt.1747@gmail.com")
    
    print("Logging in...")
    login_page = LoginPage(page)
    await login_page.login(target_account.email, target_account.password)
    
    publish_page = LaguPublishPage(page)
    await publish_page.go_to_single_publish()
    
    track_path = "/home/aaa/Downloads/Jane_Eyre_Songs/Fire Stone/Fire In The Bed.wav"
    payload = UploadPayload(
        track_path=Path(track_path),
        title="Validation Test",
        artist="Kurs",
        genre="Pop",
        songwriter_name="Kusriyah"
    )
    
    print("Filling Track Information (Step 1)...")
    await publish_page.fill_track_information(payload)
    
    # Click Selanjutnya to trigger validation
    print("Clicking Selanjutnya...")
    await page.evaluate('''() => {
        const btns = [...document.querySelectorAll('button, div, span, a')];
        const btn = btns.find(b => b.innerText && (b.innerText.trim() === 'Next' || b.innerText.trim() === 'Selanjutnya') && b.getBoundingClientRect().width > 0);
        if (btn) btn.click();
    }''')
    await asyncio.sleep(2)
    
    # Get all validation errors and print them
    errors = await page.evaluate('''() => {
        // Look for validation errors on the page. They usually have a class or are styled in red.
        // Let's search for elements with red color or elements with specific error classes or text.
        // Also look at the error modal list if visible.
        const list = [];
        // Check if error modal is open and read its contents
        const modal = document.querySelector('.semi-modal');
        if (modal) {
            list.push({ source: 'Modal Content', text: modal.innerText });
        }
        
        // Find all visible red helper/error texts
        const all = document.querySelectorAll('*');
        for (const el of all) {
            const style = window.getComputedStyle(el);
            const color = style.color;
            if ((color.includes('255, 77, 79') || color.includes('255, 0, 0') || color.includes('red')) && el.innerText && el.innerText.trim().length > 0) {
                // Only visible elements with width > 0
                if (el.getBoundingClientRect().width > 0) {
                    list.push({ source: 'Page Element (' + el.tagName + ')', text: el.innerText.trim() });
                }
            }
        }
        return list;
    }''')
    
    print(f"\nFound {len(errors)} validation errors:")
    for e in errors:
        print(f"- Source: {e['source']}")
        print(f"  Text: {e['text']}")
        
    await page.screenshot(path="validation_errors_raw.png", full_page=True)
    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
