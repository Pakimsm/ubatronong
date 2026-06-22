import asyncio
import logging
from typing import Awaitable, Callable, Optional

logger = logging.getLogger(__name__)


class Scheduler:
    def __init__(self) -> None:
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def run_interval(
        self,
        coro_factory: Callable[[], Awaitable[None]],
        interval_seconds: float,
    ) -> None:
        self._running = True
        while self._running:
            try:
                await coro_factory()
            except Exception as exc:
                logger.error("Scheduled task error: %s", exc)
            await asyncio.sleep(interval_seconds)

    def stop(self) -> None:
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()
