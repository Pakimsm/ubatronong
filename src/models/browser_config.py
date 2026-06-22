from dataclasses import dataclass


@dataclass(frozen=True)
class BrowserConfig:
    headless: bool = False
    slow_mo: int = 0
    default_timeout: float = 30_000
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
