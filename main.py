import sys
import asyncio
from pathlib import Path

from src.core.browser import PlaywrightBrowser
from src.core.account_manager import JsonAccountRepository
from src.cli.app import run_cli
from src.models.browser_config import BrowserConfig

async def main() -> None:
    # Use headless=False so we can see what the bot is doing
    config = BrowserConfig(headless=False)
    browser = PlaywrightBrowser(config)
    account_repo = JsonAccountRepository(Path("config/accounts.json"))
    
    try:
        await run_cli(browser, account_repo)
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    asyncio.run(main())
