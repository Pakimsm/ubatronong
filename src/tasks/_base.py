from src.interfaces.browser import IPage
from src.interfaces.task import ITask
from src.models.account import Account
from typing import TypeVar

_BASE = "https://www.soundon.global"

_SEL_EMAIL    = "input[name='username']"
_SEL_PASSWORD = "input[data-id='password-input']"
_SEL_SUBMIT   = "button:has-text('Log in')"

T = TypeVar("T")


class SoundOnTask(ITask[T]):
    """Base for all SoundOn tasks — provides shared login flow."""

    async def _login(self, page: IPage, account: Account) -> None:
        await page.goto(f"{_BASE}/login")
        await page.wait_for_selector(_SEL_EMAIL)
        await page.fill(_SEL_EMAIL, account.email)
        await page.fill(_SEL_PASSWORD, account.password)
        await page.click(_SEL_SUBMIT)
        await page.wait_for_navigation()
