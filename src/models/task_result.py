from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class TaskResult:
    success: bool
    message: str
    data: Optional[Any] = None
