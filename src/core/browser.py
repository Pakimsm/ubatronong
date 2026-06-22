from __future__ import annotations

from typing import Any, List, Optional

from playwright.async_api import (
    Browser,
    ElementHandle,
    Page,
    Playwright,
    async_playwright,
)

from src.interfaces.browser import IBrowser, IElement, IPage
from src.models.browser_config import BrowserConfig


class PlaywrightElement(IElement):
    def __init__(self, handle: ElementHandle) -> None:
        self._handle = handle

    async def text_content(self) -> Optional[str]:
        return await self._handle.text_content()

    async def inner_text(self) -> str:
        return await self._handle.inner_text()

    async def get_attribute(self, name: str) -> Optional[str]:
        return await self._handle.get_attribute(name)

    async def click(self) -> None:
        await self._handle.click()

    async def query_selector(self, selector: str) -> Optional[IElement]:
        handle = await self._handle.query_selector(selector)
        return PlaywrightElement(handle) if handle else None

    async def query_selector_all(self, selector: str) -> List[IElement]:
        handles = await self._handle.query_selector_all(selector)
        return [PlaywrightElement(h) for h in handles]


class PlaywrightPage(IPage):
    def __init__(self, page: Page) -> None:
        self._page = page

    async def goto(self, url: str) -> None:
        await self._page.goto(url)

    async def fill(self, selector: str, value: str) -> None:
        await self._page.fill(selector, value)

    async def click(self, selector: str, **kwargs: Any) -> None:
        await self._page.click(selector, **kwargs)

    async def text_content(self, selector: str) -> Optional[str]:
        return await self._page.text_content(selector)

    async def wait_for_selector(
        self, selector: str, timeout: float = 5_000
    ) -> None:
        await self._page.wait_for_selector(selector, timeout=timeout)

    async def wait_for_navigation(self) -> None:
        await self._page.wait_for_load_state("networkidle")

    async def query_selector(self, selector: str) -> Optional[IElement]:
        handle = await self._page.query_selector(selector)
        return PlaywrightElement(handle) if handle else None

    async def query_selector_all(self, selector: str) -> List[IElement]:
        handles = await self._page.query_selector_all(selector)
        return [PlaywrightElement(h) for h in handles]

    async def evaluate(self, expression: str, *args: Any) -> Any:
        return await self._page.evaluate(expression, *args)

    async def set_input_files(self, selector: str, path: str) -> None:
        print(f"DEBUG: PlaywrightPage.set_input_files called with selector='{selector}'")
        await self._page.set_input_files(selector, path)

    async def upload_file(self, trigger_selector: str, file_path: str) -> None:
        async with self._page.expect_file_chooser() as fc_info:
            await self._page.click(trigger_selector)
        file_chooser = await fc_info.value
        await file_chooser.set_files(file_path)

    async def screenshot(self, path: str, full_page: bool = False) -> None:
        await self._page.screenshot(path=path, full_page=full_page)

    async def current_url(self) -> str:
        return self._page.url

    async def is_visible(self, selector: str) -> bool:
        return await self._page.is_visible(selector)

    async def input_value(self, selector: str) -> str:
        return await self._page.input_value(selector)

    async def type(self, selector: str, text: str, delay: int = 0) -> None:
        await self._page.type(selector, text, delay=delay)

    async def close(self) -> None:
        await self._page.close()


class PlaywrightBrowser(IBrowser):
    def __init__(self, config: BrowserConfig) -> None:
        self._config = config
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None

    async def launch(self) -> None:
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=self._config.headless,
            slow_mo=self._config.slow_mo,
        )

    async def close(self) -> None:
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        self._browser = None
        self._playwright = None

    async def new_page(self) -> IPage:
        if not self._browser:
            raise RuntimeError("Browser not launched. Call launch() or use async with.")
        page = await self._browser.new_page(user_agent=self._config.user_agent)
        page.set_default_timeout(self._config.default_timeout)
        return PlaywrightPage(page)
