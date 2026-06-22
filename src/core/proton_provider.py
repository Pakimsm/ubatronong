"""
ProtonMailProvider: creates a real @proton.me inbox using Playwright,
verifies via a throwaway Guerrilla Mail address, then reads SoundOn codes
by logging back into Proton Mail web UI.
"""
from __future__ import annotations

import asyncio
import json
import re
import secrets
import string
from typing import Tuple

import aiohttp
from playwright.async_api import async_playwright

from src.interfaces.email_provider import IEmailProvider

_PROTON_SIGNUP = "https://account.proton.me/mail/signup?plan=free"
_PROTON_LOGIN  = "https://mail.proton.me/login"

_GUERRILLA_API = "https://api.guerrillamail.com/ajax.php"
_GUERRILLA_UA  = "Mozilla/5.0 (compatible; SoundOnBot/1.0)"

# Swiss baby names for realistic usernames
_SWISS_NAMES = [
    "hans", "peter", "urs", "markus", "stefan", "thomas", "michael", "andreas",
    "christian", "daniel", "simon", "lukas", "tobias", "david", "johannes",
    "matthias", "florian", "felix", "dominik", "marco", "fabian", "reto",
    "anna", "maria", "sarah", "laura", "julia", "lisa", "nicole", "sandra",
    "christine", "monika", "susanne", "barbara", "petra", "claudia", "andrea",
    "sabrina", "michelle", "nadine", "stefanie", "katharina", "eva", "franziska",
    "luca", "noah", "leon", "elias", "finn", "ben", "jonas", "jan", "tim", "max",
    "emma", "mia", "sofia", "lena", "lea", "hannah", "emilia", "leonie", "jana",
    "jean", "pierre", "marc", "alain", "mathieu", "julien", "nicolas",
    "marie", "sophie", "claire", "isabelle", "celine", "nathalie",
    "chiara", "valentina", "giulia", "francesca", "elena", "paolo", "giorgio",
]


def _random_username() -> str:
    name = secrets.choice(_SWISS_NAMES)
    suffix = "".join(secrets.choice(string.digits) for _ in range(3))
    return f"{name}{suffix}"


def _random_password() -> str:
    chars = string.ascii_letters + string.digits + "!@#$"
    return "".join(secrets.choice(chars) for _ in range(14))


class ProtonMailProvider(IEmailProvider):
    """
    Creates a @proton.me account using Playwright automation.
    Uses a temporary Guerrilla Mail address to pass Proton's human verification.
    Reads the SoundOn verification code by logging into Proton Mail web UI.
    """

    async def create_inbox(self) -> Tuple[str, str]:
        """
        Returns (proton_email, token) where token = JSON {"email": ..., "password": ...}.
        """
        username = _random_username()
        password = _random_password()
        proton_email = f"{username}@proton.me"

        # Step 1: create a throwaway inbox for Proton's human verification
        guerrilla_email, guerrilla_token = await _guerrilla_create()

        # Step 2: automate Proton signup
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, slow_mo=150)
            page = await browser.new_page()
            try:
                await _proton_signup(
                    page, username, password,
                    guerrilla_email, guerrilla_token,
                )
            finally:
                await browser.close()

        token = json.dumps({"email": proton_email, "password": password})
        return proton_email, token

    async def wait_for_code(self, token: str, timeout: int = 300) -> str:
        creds = json.loads(token)
        email    = creds["email"]
        password = creds["password"]

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, slow_mo=100)
            page = await browser.new_page()
            try:
                code = await _proton_read_inbox(page, email, password, timeout)
            finally:
                await browser.close()

        return code


# ------------------------------------------------------------------ helpers

async def _guerrilla_create() -> Tuple[str, str]:
    async with aiohttp.ClientSession(headers={"User-Agent": _GUERRILLA_UA}) as s:
        async with s.get(f"{_GUERRILLA_API}?f=get_email_address") as resp:
            data = await resp.json(content_type=None)
    return data["email_addr"], data["sid_token"]


async def _guerrilla_poll_code(token: str, timeout: int = 120) -> str:
    from src.core.email_provider import _extract_code
    deadline = asyncio.get_event_loop().time() + timeout
    seen: set[str] = set()

    async with aiohttp.ClientSession(headers={"User-Agent": _GUERRILLA_UA}) as s:
        while asyncio.get_event_loop().time() < deadline:
            url = f"{_GUERRILLA_API}?f=get_email_list&offset=0&sid_token={token}"
            async with s.get(url) as resp:
                data = await resp.json(content_type=None)

            for msg in data.get("list", []):
                mail_id = str(msg["mail_id"])
                # check subject first
                code = _extract_code(msg.get("mail_subject", "") or "")
                if code:
                    return code
                if mail_id in seen:
                    continue
                seen.add(mail_id)
                async with s.get(f"{_GUERRILLA_API}?f=fetch_email&email_id={mail_id}&sid_token={token}") as r2:
                    detail = await r2.json(content_type=None)
                body = re.sub(r"<[^>]+>", " ", detail.get("mail_body", "") or "")
                code = _extract_code(body)
                if code:
                    return code

            await asyncio.sleep(5)

    raise TimeoutError("Proton human-verification code not received")


async def _proton_signup(page, username: str, password: str,
                          verif_email: str, verif_token: str) -> None:
    await page.goto(_PROTON_SIGNUP, timeout=30_000)
    await page.wait_for_timeout(5_000)

    # get email iframe
    email_frame = next((f for f in page.frames if "Name=email" in f.url), None)
    if not email_frame:
        raise RuntimeError("Proton email iframe not found")

    # fill password fields (confirm password appears after focus)
    await page.fill("#password", password)
    await page.wait_for_timeout(400)
    pw_inputs = await page.query_selector_all('input[type="password"]')
    if len(pw_inputs) >= 2:
        await pw_inputs[1].fill(password)

    # fill username in iframe
    await email_frame.type("#username", username, delay=80)
    await page.wait_for_timeout(1_000)

    # submit
    await page.click('button[type="submit"]', timeout=10_000)

    # dismiss upsell modal
    try:
        await page.wait_for_selector("text=No, thanks", timeout=15_000)
        await page.click("text=No, thanks")
    except Exception:
        pass

    # handle human verification modal
    try:
        await page.wait_for_selector("text=Human Verification", timeout=15_000)
        # fill throwaway email
        await page.fill('input[id*="email"], input[placeholder*="email" i], dialog input[type="text"], dialog input[type="email"]', verif_email)
        await page.click("button:has-text('Get verification code')")

        # get code from guerrilla mail
        code = await _guerrilla_poll_code(verif_token)
        # enter verification code
        await page.wait_for_selector('input[placeholder*="code" i], input[id*="code"]', timeout=15_000)
        await page.fill('input[placeholder*="code" i], input[id*="code"]', code)
        await page.click("button:has-text('Verify')")
    except Exception:
        pass

    # wait for redirect to inbox
    await page.wait_for_function(
        "() => !window.location.href.includes('/signup')",
        timeout=60_000,
    )


async def _proton_read_inbox(page, email: str, password: str, timeout: int) -> str:
    from src.core.email_provider import _extract_code

    await page.goto(_PROTON_LOGIN, timeout=30_000)
    await page.wait_for_timeout(3_000)

    # fill login form
    await page.fill('input[id="username"], input[name="username"]', email.replace("@proton.me", ""))
    await page.fill('input[id="password"], input[type="password"]', password)
    await page.click('button[type="submit"]')
    await page.wait_for_timeout(5_000)

    # wait until we're in the inbox
    await page.wait_for_function(
        "() => window.location.href.includes('/mail') || window.location.href.includes('/inbox')",
        timeout=30_000,
    )

    deadline = asyncio.get_event_loop().time() + timeout
    seen: set[str] = set()

    while asyncio.get_event_loop().time() < deadline:
        await page.reload()
        await page.wait_for_timeout(3_000)

        # grab all email rows
        rows = await page.query_selector_all('[data-shortcut-target="item-container"], [class*="conversation-item"], li[class*="message"]')
        for row in rows:
            subject = await row.evaluate("el => el.innerText")
            code = _extract_code(subject)
            if code:
                return code

            row_id = await row.evaluate("el => el.getAttribute('data-element-id') || el.getAttribute('data-id') || ''")
            if row_id in seen:
                continue
            seen.add(row_id)

            await row.click()
            await page.wait_for_timeout(2_000)
            body = await page.evaluate("() => document.querySelector('[class*=\"message-content\"], [class*=\"messageContent\"], .proton-message-content')?.innerText || ''")
            code = _extract_code(body)
            if code:
                return code

        await asyncio.sleep(10)

    raise TimeoutError("SoundOn verification code not found in Proton inbox")
