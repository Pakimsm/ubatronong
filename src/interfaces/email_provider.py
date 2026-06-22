from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Tuple


class IEmailProvider(ABC):
    @abstractmethod
    async def create_inbox(self) -> Tuple[str, str]:
        """Create a disposable inbox. Returns (email_address, auth_token)."""
        ...

    @abstractmethod
    async def wait_for_code(self, token: str, timeout: int = 120) -> str:
        """Poll inbox until a verification code arrives. Returns the code string."""
        ...
