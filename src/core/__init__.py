"""Paket core (browser, runner, repo, logger, scheduler).

Sengaja TANPA eager-import. Sebelumnya `from .browser import PlaywrightBrowser`
membuat impor ringan seperti `from src.core.logger import setup_logger` ikut
menyeret Playwright. Konsumen meng-import submodul langsung, mis.:
    from src.core.browser import PlaywrightBrowser
    from src.core.logger import setup_logger
"""
