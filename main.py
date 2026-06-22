import os
import asyncio
from pathlib import Path

from dotenv import load_dotenv

from src.core.account_manager import JsonAccountRepository
from src.cli.app import run_cli
from src.interfaces.browser import IBrowser
from src.models.browser_config import BrowserConfig


def build_browser(config: BrowserConfig) -> IBrowser:
    """Pilih backend browser via env BROWSER_BACKEND ('dolphin' | 'playwright')."""
    backend = os.getenv("BROWSER_BACKEND", "dolphin").strip().lower()

    if backend == "dolphin":
        from src.core.dolphin_browser import DolphinBrowser
        return DolphinBrowser(
            config,
            api_base=os.getenv("DOLPHIN_API_BASE", "http://localhost:3001/v1.0"),
            api_token=os.getenv("DOLPHIN_API_TOKEN") or None,
        )

    from src.core.browser import PlaywrightBrowser
    return PlaywrightBrowser(config)


async def main() -> None:
    load_dotenv()
    # headless=False supaya alurnya kelihatan (dan Dolphin memang non-headless)
    config = BrowserConfig(headless=False)
    browser = build_browser(config)
    account_repo = JsonAccountRepository(Path("config/accounts.json"))

    try:
        await run_cli(browser, account_repo)
    except KeyboardInterrupt:
        print("\nExiting...")


if __name__ == "__main__":
    asyncio.run(main())
