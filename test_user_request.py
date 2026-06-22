import asyncio
from pathlib import Path
from src.core.browser import PlaywrightBrowser
from src.core.account_manager import JsonAccountRepository
from src.models.browser_config import BrowserConfig
from src.models.upload_payload import UploadPayload
from src.tasks.upload_album import UploadAlbumTask

async def run_test():
    config = BrowserConfig(headless=True)
    browser = PlaywrightBrowser(config)
    await browser.launch()
    page = await browser.new_page()
    
    account_repo = JsonAccountRepository(Path("config/accounts.json"))
    accounts = account_repo.get_all()
    target_account = next(a for a in accounts if a.email == "tgobox.jkt.1747@gmail.com")
    
    payload = UploadPayload(
        track_path=Path("/home/aaa/Downloads/Jane_Eyre_Songs/Fire Stone"),
        cover_path=Path("/home/aaa/.gemini/antigravity-cli/brain/1dbfe5da-4ecd-4f07-8245-73d55f0fbb7d/cover_art_1781667614560.jpg"),
        title="Fire Stone",
        title_language="English",
        genre="Country",
        artist="Kurs",
        release_date=""
    )
    task = UploadAlbumTask(payload)
    
    try:
        print("Starting task execution...")
        # Run the album creation
        print("DEBUG: Executing upload album task...")
        result = await task.execute(page, target_account)
        
        print("Task Result:")
        print(result)
        
        # Take a screenshot of what the track page looks like!
        print("\nDEBUG: Taking screenshot of the track upload page...")
        await page._page.screenshot(path="debug_track_page.png", full_page=True)
        
        # Check drafts page
        print("\nDEBUG: Checking drafts page...")
        await page._page.goto("https://www.soundon.global/library/list?lang=id&type=drafts", wait_until="networkidle")
        await asyncio.sleep(5)
        await page._page.screenshot(path="drafts_final.png", full_page=True)
        text = await page._page.evaluate("document.body.innerText")
        if "Fire Stone" in text:
            print("Found Fire Stone in the drafts page!")
        else:
            print("Could not find Fire Stone in the drafts page.")
            
    except Exception as e:
        print("Task Result:")
        print(False)
        print(e)
    finally:
        # Take screenshot of final state
        print("\\nDEBUG: Taking screenshots of the final state...")
        try:
            await page._page.screenshot(path="debug_final.png")
        except:
            pass
        await asyncio.sleep(1)
    
    await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
