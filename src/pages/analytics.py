import asyncio
from src.pages.base import BasePage
from src.constants import BASE_URL as _BASE

class AnalyticsPage(BasePage):
    async def extract_streams(self) -> dict:
        # Assuming '/analytics' is the dashboard for streams
        await self.navigate(f"{_BASE}/analytics")
        try:
            await self.wait_for_element("[class*='stream'], [class*='metric']", timeout=20000)
        except Exception:
            raise Exception("Analytics page failed to load or metrics not found.")
            
        streams = await self.page.evaluate("""() => {
            // Find an element that looks like it holds stream counts
            // This relies on the live DOM structure, fallback to 0
            const els = [...document.querySelectorAll('div, span, h2')];
            const streamLabel = els.find(el => el.innerText && el.innerText.toLowerCase().includes('total stream'));
            if (streamLabel && streamLabel.nextElementSibling) {
                return streamLabel.nextElementSibling.innerText.trim();
            }
            // fallback generic selector
            const streamEl = document.querySelector('[class*="stream-count"]');
            return streamEl ? streamEl.innerText.trim() : '0';
        }""")
        
        return {"total_streams": streams}
