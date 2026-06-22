from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from src.interfaces.browser import IPage
from src.models.account import Account

T = TypeVar("T")


class ITask(ABC, Generic[T]):
    """Single unit of work executed per account inside a browser page."""

    @abstractmethod
    async def execute(self, page: IPage, account: Account) -> T: ...
