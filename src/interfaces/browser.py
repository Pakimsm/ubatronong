from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, List, Optional


class IElement(ABC):
    @abstractmethod
    async def text_content(self) -> Optional[str]: ...

    @abstractmethod
    async def inner_text(self) -> str: ...

    @abstractmethod
    async def get_attribute(self, name: str) -> Optional[str]: ...

    @abstractmethod
    async def click(self) -> None: ...

    @abstractmethod
    async def query_selector(self, selector: str) -> Optional["IElement"]: ...

    @abstractmethod
    async def query_selector_all(self, selector: str) -> List["IElement"]: ...


class IPage(ABC):
    @abstractmethod
    async def goto(self, url: str) -> None: ...

    @abstractmethod
    async def fill(self, selector: str, value: str) -> None: ...

    @abstractmethod
    async def click(self, selector: str, **kwargs: Any) -> None: ...

    @abstractmethod
    async def text_content(self, selector: str) -> Optional[str]: ...

    @abstractmethod
    async def wait_for_selector(
        self, selector: str, timeout: float = 5_000
    ) -> None: ...

    @abstractmethod
    async def wait_for_navigation(self) -> None: ...

    @abstractmethod
    async def query_selector(self, selector: str) -> Optional[IElement]: ...

    @abstractmethod
    async def query_selector_all(self, selector: str) -> List[IElement]: ...

    @abstractmethod
    async def evaluate(self, expression: str, *args: Any) -> Any: ...

    @abstractmethod
    async def set_input_files(self, selector: str, path: str) -> None: ...

    @abstractmethod
    async def upload_file(self, trigger_selector: str, file_path: str) -> None:
        """Click trigger_selector then set file via the file chooser that opens."""
        ...

    @abstractmethod
    async def screenshot(self, path: str, full_page: bool = False) -> None: ...

    @abstractmethod
    async def current_url(self) -> str: ...

    @abstractmethod
    async def is_visible(self, selector: str) -> bool: ...

    @abstractmethod
    async def input_value(self, selector: str) -> str: ...

    @abstractmethod
    async def type(self, selector: str, text: str, delay: int = 0) -> None: ...

    @abstractmethod
    async def close(self) -> None: ...


class IBrowser(ABC):
    @abstractmethod
    async def launch(self) -> None: ...

    @abstractmethod
    async def close(self) -> None: ...

    @abstractmethod
    async def new_page(self) -> IPage: ...

    async def __aenter__(self) -> IBrowser:
        await self.launch()
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()
