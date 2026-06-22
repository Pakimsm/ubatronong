from abc import ABC, abstractmethod
from typing import List

from src.models.account import Account


class IAccountRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[Account]: ...

    @abstractmethod
    def get_active(self) -> List[Account]: ...

    @abstractmethod
    def save(self, account: Account) -> None: ...

    @abstractmethod
    def delete(self, account_id: int) -> None: ...
