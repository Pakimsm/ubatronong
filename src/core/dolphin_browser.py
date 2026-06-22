from __future__ import annotations

from typing import Dict, Optional

import aiohttp
from playwright.async_api import Browser, Playwright, async_playwright

from src.core.browser import PlaywrightPage
from src.interfaces.browser import IBrowser, IPage
from src.models.account import Account
from src.models.browser_config import BrowserConfig


class DolphinPage(PlaywrightPage):
    """Page Dolphin: saat ditutup, sekalian hentikan profil Dolphin-nya."""

    def __init__(self, page, on_close) -> None:
        super().__init__(page)
        self._on_close = on_close

    async def close(self) -> None:
        try:
            await super().close()
        finally:
            await self._on_close()


class DolphinBrowser(IBrowser):
    """Backend anti-deteksi: tiap akun -> satu profil Dolphin Anty.

    Tidak me-launch Chromium sendiri. Dolphin yang membuka browser (lengkap dengan
    fingerprint + proxy per profil), lalu Playwright menempel via CDP. Fingerprint
    spoofing ditangani Dolphin, jadi init-script stealth manual tidak diperlukan.
    """

    def __init__(
        self,
        config: BrowserConfig,
        api_base: str = "http://localhost:3001/v1.0",
        api_token: Optional[str] = None,
    ) -> None:
        self._config = config
        self._api_base = api_base.rstrip("/")
        self._headers = {"Authorization": f"Bearer {api_token}"} if api_token else {}
        self._playwright: Optional[Playwright] = None
        # profile_id -> koneksi CDP yang sedang aktif
        self._active: Dict[str, Browser] = {}

    async def launch(self) -> None:
        self._playwright = await async_playwright().start()

    async def close(self) -> None:
        # Hentikan profil yang mungkin masih tersisa (mis. task error sebelum page.close)
        for profile_id in list(self._active):
            await self._disconnect(profile_id)
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None

    async def new_page(self, account: Optional[Account] = None) -> IPage:
        if self._playwright is None:
            raise RuntimeError("Browser belum di-launch. Pakai 'async with' atau panggil launch().")
        if account is None or not account.dolphin_profile_id:
            raise RuntimeError(
                f"Akun '{getattr(account, 'email', '?')}' tidak punya dolphin_profile_id. "
                "Isi ID profil Dolphin lewat menu 'Tambah Akun' atau config/accounts.json."
            )

        profile_id = account.dolphin_profile_id
        port, ws_endpoint = await self._start_profile(profile_id)

        cdp = await self._playwright.chromium.connect_over_cdp(f"ws://127.0.0.1:{port}{ws_endpoint}")
        self._active[profile_id] = cdp

        # Profil Dolphin sudah punya context (biasanya sudah ter-login). Pakai yang ada.
        context = cdp.contexts[0] if cdp.contexts else await cdp.new_context()
        page = context.pages[0] if context.pages else await context.new_page()
        page.set_default_timeout(self._config.default_timeout)

        async def _cleanup() -> None:
            await self._disconnect(profile_id)

        return DolphinPage(page, _cleanup)

    # --- Dolphin Local API ---------------------------------------------------

    async def _start_profile(self, profile_id: str) -> tuple[int, str]:
        url = f"{self._api_base}/browser_profiles/{profile_id}/start?automation=1"
        try:
            async with aiohttp.ClientSession(headers=self._headers) as session:
                async with session.get(url) as resp:
                    data = await resp.json()
        except aiohttp.ClientError as exc:
            raise RuntimeError(
                f"Tidak bisa menghubungi Dolphin Anty di {self._api_base}. "
                f"Pastikan aplikasi Dolphin berjalan. Detail: {exc}"
            ) from exc

        automation = data.get("automation") if isinstance(data, dict) else None
        if not automation or "port" not in automation:
            raise RuntimeError(f"Gagal start profil Dolphin '{profile_id}': {data}")
        return int(automation["port"]), automation["wsEndpoint"]

    async def _disconnect(self, profile_id: str) -> None:
        cdp = self._active.pop(profile_id, None)
        if cdp is not None:
            try:
                await cdp.close()
            except Exception:
                pass
        await self._stop_profile(profile_id)

    async def _stop_profile(self, profile_id: str) -> None:
        url = f"{self._api_base}/browser_profiles/{profile_id}/stop"
        try:
            async with aiohttp.ClientSession(headers=self._headers) as session:
                async with session.get(url) as resp:
                    await resp.read()
        except Exception:
            # cleanup best-effort; jangan gagalkan alur hanya karena stop gagal
            pass
