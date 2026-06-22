import asyncio
from pathlib import Path
from src.core.browser import PlaywrightBrowser
from src.core.account_manager import JsonAccountRepository
from src.models.browser_config import BrowserConfig
from src.pages.login import LoginPage
from src.pages.lagu_publish import LaguPublishPage

async def main():
    # Run in headless mode to test
    config = BrowserConfig(headless=True)
    browser = PlaywrightBrowser(config)
    await browser.launch()
    page = await browser.new_page()
    
    account_repo = JsonAccountRepository(Path("config/accounts.json"))
    target_account = next(a for a in account_repo.get_all() if a.email == "tgobox.jkt.1747@gmail.com")
    
    login_page = LoginPage(page)
    await login_page.login(target_account.email, target_account.password)
    
    publish_page = LaguPublishPage(page)
    await publish_page.go_to_single_publish()
    
    # Try setting input files and see what selector is printed and if it succeeds
    print("Setting input files...")
    track_path = "/home/aaa/Downloads/Jane_Eyre_Songs/Fire Stone/Fire In The Bed.wav"
    try:
        await page.set_input_files("input[type='file'][accept*='.mp3']", track_path)
        print("Success!")
    except Exception as e:
        print("Failed:", e)
        
    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
