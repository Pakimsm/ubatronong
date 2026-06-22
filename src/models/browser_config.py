from dataclasses import dataclass


@dataclass(frozen=True)
class BrowserConfig:
    headless: bool = False
    # slow_mo kecil bikin gerakan tidak instan (lebih mirip manusia) tanpa bikin lemot
    slow_mo: int = 40
    default_timeout: float = 30_000
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    )
    # Lokalitas realistis untuk akun Indonesia
    locale: str = "id-ID"
    timezone_id: str = "Asia/Jakarta"
    viewport_width: int = 1366
    viewport_height: int = 768
