import asyncio
from typing import Optional
from src.interfaces.browser import IPage
from src.core.logger import setup_logger

logger = setup_logger("publish")


class BasePage:
    def __init__(self, page: IPage):
        self.page = page

    async def dismiss_popups(self) -> None:
        """Dismiss common annoyances like survey popups or announcements."""
        try:
            await self.page.evaluate('''() => {
                // Click semi-modal close buttons
                document.querySelectorAll(".semi-modal-close, .semi-modal-close-button, .semi-modal-close-btn").forEach(btn => btn.click());
                
                // Find and click any buttons containing close words
                const closeWords = ['nanti saja', 'not now', 'tutup', 'got it', 'nanti', 'close', 'maybe later', 'nanti saja (remind me later)', 'remind me later'];
                document.querySelectorAll("button, span, div, a").forEach(el => {
                    if (el.innerText) {
                        const txt = el.innerText.trim().toLowerCase();
                        if (closeWords.includes(txt) && el.getBoundingClientRect().width > 0) {
                            el.click();
                        }
                    }
                });
            }''')
            await asyncio.sleep(1)
        except Exception:
            pass

    async def navigate(self, url: str) -> None:
        await self.page.goto(url)
        await asyncio.sleep(1)
        await self.dismiss_popups()

    async def wait_for_element(self, selector: str, timeout: int = 15000) -> None:
        await self.page.wait_for_selector(selector, timeout=timeout)

    async def is_visible(self, selector: str) -> bool:
        try:
            return await self.page.is_visible(selector)
        except Exception:
            return False

    async def click(self, selector: str, timeout: int = 10000) -> None:
        await self.wait_for_element(selector, timeout=timeout)
        await self.page.click(selector, timeout=timeout)
        await asyncio.sleep(0.5)

    async def fill(self, selector: str, value: str) -> None:
        await self.wait_for_element(selector)
        await self.page.fill(selector, value)

    async def fill_react(self, selector: str, value: str) -> None:
        """Ketik seperti manusia + picu event React onChange. Lewat kontrak IPage
        (tanpa menyentuh objek Playwright konkret)."""
        await self.wait_for_element(selector)
        await self.page.type_human(selector, value)

    async def select_semi(self, index: int, value: str) -> None:
        """Interact with Semi UI dropdowns lewat kontrak IPage."""
        await self.page.dispatch_select_option(".semi-select", index, value)

    async def click_radio_option(self, label_text: str, option_text: str) -> bool:
        """Finds a form field by label_text (searching for the shortest containing leaf element), 
        traverses up its parent chain, and clicks the option containing option_text."""
        logger.info(f"Clicking radio/button option '{option_text}' for field '{label_text}'...")
        try:
            success = await self.page.evaluate('''([lbl, opt]) => {
                const elements = [...document.querySelectorAll("label, span, div, p, button")];
                const match = elements
                    .filter(el => el.innerText && el.innerText.includes(lbl) && el.getBoundingClientRect().width > 0)
                    .sort((a, b) => a.innerText.length - b.innerText.length)[0];
                    
                if (match) {
                    let parent = match.parentElement;
                    for (let i = 0; i < 5 && parent; i++) {
                        const targets = [...parent.querySelectorAll("label, button, div, span, input")];
                        const target = targets.find(el => el.innerText && el.innerText.trim() === opt && el.getBoundingClientRect().height > 0);
                        if (target) {
                            target.dispatchEvent(new MouseEvent("mousedown", {bubbles: true}));
                            target.dispatchEvent(new MouseEvent("mouseup", {bubbles: true}));
                            target.click();
                            return true;
                        }
                        parent = parent.parentElement;
                    }
                }
                return false;
            }''', [label_text, option_text])
            return bool(success)
        except Exception as e:
            logger.debug(f"Error clicking radio/button option '{option_text}' for '{label_text}': {e}")
            return False
