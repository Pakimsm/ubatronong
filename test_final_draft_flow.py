import asyncio
from pathlib import Path
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
    
    account_repo = JsonAccountRepository(Path("config/accounts.json"))
    target_account = next(a for a in account_repo.get_all() if a.email == "tgobox.jkt.1747@gmail.com")
    
    # Login
    login_page = LoginPage(page)
    await login_page.login(target_account.email, target_account.password)
    
    # Go to single publish
    publish_page = LaguPublishPage(page)
    await publish_page.go_to_single_publish()
    
    payload = UploadPayload(
        track_path=Path("/home/aaa/Downloads/Jane_Eyre_Songs/Fire Stone/Fire In The Bed.wav"),
        title="Fire In The Bed",
        artist="Kurs",
        genre="Pop",
        songwriter_name="Kusriyah"
    )
    
    # Start upload
    print("Uploading audio...")
    await page.set_input_files("input[type='file'][accept*='.mp3']", str(payload.track_path))
    
    # Wait for Upload complete
    print("Waiting for upload to complete...")
    await page._page.wait_for_selector("text='Upload complete'", state="visible", timeout=1800000)
    await asyncio.sleep(2)
    
    # Fill fields
    print("Filling form fields...")
    # 1. Title
    try:
        input_selector = await page._page.evaluate('''() => {
            const labels = [...document.querySelectorAll('label, span, div')];
            const judulLabel = labels.find(l => l.innerText && (l.innerText.trim() === 'Judul' || l.innerText.toLowerCase().includes('release title') || l.innerText.toLowerCase().includes('track title')));
            if (judulLabel) {
                let parent = judulLabel.parentElement;
                while (parent && parent.tagName !== 'BODY') {
                    const inputs = parent.querySelectorAll('input[type="text"]');
                    if (inputs.length > 0) {
                        inputs[0].id = 'soundon-title-input-hack';
                        return '#soundon-title-input-hack';
                    }
                    parent = parent.parentElement;
                }
            }
            return 'input[type="text"]';
        }''')
        title_input = page._page.locator(input_selector).first
        await title_input.click(force=True)
        await title_input.fill("")
        await title_input.type(payload.title, delay=50)
    except Exception as e:
        print("Failed title:", e)
        
    # 2. Artist modal
    try:
        await page._page.evaluate('''() => {
            const mainArtistsDiv = document.getElementById("mainArtists");
            if (mainArtistsDiv) {
                const btn = mainArtistsDiv.querySelector("button");
                if (btn) btn.click();
            }
        }''')
        await asyncio.sleep(2)
        await page.click("#artistProfile")
        await asyncio.sleep(1)
        await page._page.evaluate('''(name) => {
            const container = document.getElementById("artistProfile");
            if (!container) return;
            const input = container.querySelector("input");
            if (input) {
                input.focus();
                const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value").set;
                setter.call(input, name);
                input.dispatchEvent(new Event("input", {bubbles: true}));
                input.dispatchEvent(new Event("change", {bubbles: true}));
            }
        }''', payload.artist)
        await asyncio.sleep(2)
        await page._page.evaluate('''(name) => {
            const options = [...document.querySelectorAll("[class*='target-option']")];
            const match = options.find(o => o.getAttribute("artistname")?.toLowerCase() === name.toLowerCase());
            if (match) match.click();
        }''', payload.artist)
        await asyncio.sleep(1)
        await page._page.evaluate('''() => {
            const modal = document.querySelector(".so-form-modal");
            if (!modal) return;
            const buttons = [...modal.querySelectorAll("button")];
            const kirim = buttons.find(b => b.innerText && /kirim|submit|simpan|save/i.test(b.innerText));
            if (kirim) kirim.click();
        }''')
        await asyncio.sleep(2)
    except Exception as e:
        print("Failed artist select:", e)
        
    # Wait to see if it redirects and get the error message or text on the page
    print("Waiting 10 seconds to observe page state/redirect...")
    await asyncio.sleep(10)
    
    url = await page.current_url()
    print("Final URL:", url)
    
    # Save final screenshot
    await page.screenshot(path="final_debug_page.png", full_page=True)
    print("Saved final_debug_page.png")
    
    # Check for any error messages or toast notices on screen
    toasts = await page.evaluate('''() => {
        const notices = [...document.querySelectorAll(".semi-toast, .semi-notification, [class*='toast'], [class*='notification'], .soundon-formik-field-error")];
        return notices.map(n => n.innerText);
    }''')
    print("Visible error/notification texts:", toasts)
    
    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
