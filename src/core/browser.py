from __future__ import annotations

import asyncio
import random
from typing import Any, List, Optional

from playwright.async_api import (
    Browser,
    BrowserContext,
    ElementHandle,
    Page,
    Playwright,
    async_playwright,
)

from src.interfaces.browser import IBrowser, IElement, IPage
from src.models.browser_config import BrowserConfig

# Script disuntik sebelum setiap halaman load untuk menyamarkan sidik-jari otomasi
# (navigator.webdriver, chrome runtime, plugins, languages, dll).
_STEALTH_INIT_JS = """
(() => {
  Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
  Object.defineProperty(navigator, 'languages', { get: () => ['id-ID', 'id', 'en-US'] });
  Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
  window.chrome = window.chrome || { runtime: {} };
  const origQuery = window.navigator.permissions && window.navigator.permissions.query;
  if (origQuery) {
    window.navigator.permissions.query = (p) =>
      p && p.name === 'notifications'
        ? Promise.resolve({ state: Notification.permission })
        : origQuery(p);
  }
  const getParam = WebGLRenderingContext.prototype.getParameter;
  WebGLRenderingContext.prototype.getParameter = function (p) {
    if (p === 37445) return 'Intel Inc.';
    if (p === 37446) return 'Intel Iris OpenGL Engine';
    return getParam.apply(this, [p]);
  };
})();
"""


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
        self, selector: str, timeout: float = 5_000, state: str = "visible"
    ) -> None:
        await self._page.wait_for_selector(selector, timeout=timeout, state=state)

    async def wait_for_navigation(self) -> None:
        await self._page.wait_for_load_state("networkidle")

    async def wait_for_url(self, url_pattern: str, timeout: float = 15_000) -> None:
        await self._page.wait_for_url(url_pattern, timeout=timeout)

    async def content(self) -> str:
        return await self._page.content()

    async def keyboard_type(self, text: str) -> None:
        await self._page.keyboard.type(text)

    def locator(self, selector: str) -> Any:
        return self._page.locator(selector)

    async def query_selector(self, selector: str) -> Optional[IElement]:
        handle = await self._page.query_selector(selector)
        return PlaywrightElement(handle) if handle else None

    async def query_selector_all(self, selector: str) -> List[IElement]:
        handles = await self._page.query_selector_all(selector)
        return [PlaywrightElement(h) for h in handles]

    async def evaluate(self, expression: str, *args: Any) -> Any:
        return await self._page.evaluate(expression, *args)

    async def set_input_files(self, selector: str, path: str) -> None:
        await self._page.set_input_files(selector, path)

    async def upload_file(
        self,
        trigger_selector: str,
        file_path: str,
        use_last: bool = False,
        force: bool = False,
    ) -> None:
        locator = self._page.locator(trigger_selector)
        target = locator.last if use_last else locator.first
        async with self._page.expect_file_chooser() as fc_info:
            await target.click(force=force)
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

    async def type_human(self, selector: str, text: str) -> None:
        locator = self._page.locator(selector).first
        await locator.click()
        await locator.fill("")  # bersihkan dulu (aman untuk React)
        for ch in text:
            await locator.press_sequentially(ch, delay=random.randint(45, 160))
            # sesekali jeda lebih panjang seperti orang berpikir
            if random.random() < 0.07:
                await asyncio.sleep(random.uniform(0.2, 0.5))
        await locator.evaluate(
            """el => {
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
            }"""
        )

    async def dispatch_select_option(self, container_selector: str, index: int, value: str) -> None:
        selects = await self._page.query_selector_all(container_selector)
        if index >= len(selects):
            raise IndexError(f"Cannot find '{container_selector}' at index {index}")
        await selects[index].click()
        await asyncio.sleep(random.uniform(0.4, 0.9))
        await self._page.evaluate(
            """([val]) => {
                const opt = [...document.querySelectorAll('.semi-select-option')]
                    .find(el => el.innerText.trim() === val || el.innerText.trim().includes(val));
                if (opt) opt.click();
            }""",
            [value],
        )
        await asyncio.sleep(random.uniform(0.2, 0.5))

    async def close(self) -> None:
        await self._page.close()


class PlaywrightBrowser(IBrowser):
    def __init__(self, config: BrowserConfig) -> None:
        self._config = config
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._contexts: List[BrowserContext] = []

    async def launch(self) -> None:
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=self._config.headless,
            slow_mo=self._config.slow_mo,
            args=[
                # hilangkan flag "Chrome dikendalikan software otomasi"
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-infobars",
                "--disable-dev-shm-usage",
                "--start-maximized",
            ],
            ignore_default_args=["--enable-automation"],
        )

    async def close(self) -> None:
        for ctx in self._contexts:
            try:
                await ctx.close()
            except Exception:
                pass
        self._contexts.clear()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        self._browser = None
        self._playwright = None

    async def new_page(self, account: Any = None) -> IPage:
        # Backend Chromium generik: identitas tidak terikat akun -> account diabaikan.
        if not self._browser:
            raise RuntimeError("Browser not launched. Call launch() or use async with.")
        # Context terpisah per akun: locale/timezone/viewport realistis + stealth.
        context = await self._browser.new_context(
            user_agent=self._config.user_agent,
            locale=self._config.locale,
            timezone_id=self._config.timezone_id,
            viewport={"width": self._config.viewport_width, "height": self._config.viewport_height},
            device_scale_factor=1,
            is_mobile=False,
            has_touch=False,
        )
        await context.add_init_script(_STEALTH_INIT_JS)
        self._contexts.append(context)
        page = await context.new_page()
        page.set_default_timeout(self._config.default_timeout)
        return PlaywrightPage(page)
