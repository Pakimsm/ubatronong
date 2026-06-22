import asyncio
from src.pages.base import BasePage
from src.tasks._base import _BASE

class WithdrawPage(BasePage):
    async def get_balance(self) -> str:
        await self.navigate(f"{_BASE}/analytics/earnings")
        try:
            await self.wait_for_element("[class*='balance']", timeout=15000)
            if not await self.is_visible("[class*='balance']"):
                return "0.00"
            return await self.page.evaluate("() => document.querySelector('[class*=\"balance\"]').innerText")
        except Exception:
            return "0.00"
        
    async def withdraw_all(self) -> bool:
        try:
            await self.click("button:has-text('Withdraw')")
            await asyncio.sleep(2)
            if not await self.is_visible("text=Confirm"):
                raise Exception("Withdrawal modal did not appear.")
                
            await self.click("button:has-text('Confirm')")
            return True
        except Exception:
            return False
