from typing import TypeVar

from src.interfaces.browser import IPage
from src.interfaces.task import ITask
from src.models.account import Account
from src.constants import BASE_URL as _BASE  # re-export untuk kompatibilitas

T = TypeVar("T")


class SoundOnTask(ITask[T]):
    """Base for all SoundOn tasks — provides the single shared login entrypoint."""

    async def _login(self, page: IPage, account: Account) -> bool:
        """Satu-satunya jalur login. Mendelegasikan ke LoginPage agar selector &
        verifikasi state tidak terduplikasi di banyak tempat (DRY).
        Import di dalam fungsi untuk menghindari circular import (login.py -> _base)."""
        from src.pages.login import LoginPage

        return await LoginPage(page).login(account.email, account.password)
