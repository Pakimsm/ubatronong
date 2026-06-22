from __future__ import annotations

import asyncio
import re
import secrets
import string
from typing import Tuple

import aiohttp

from src.interfaces.email_provider import IEmailProvider

_MAILTM_API = "https://api.mail.tm"
_MAILTM_DOMAIN = "web-library.net"

# SoundOn sends alphanumeric codes like "KXD2CW" (6 chars, uppercase)
# Pattern: 4-8 uppercase alphanumeric chars that look like a code (not common words)
_CODE_RE = re.compile(r"\b([A-Z0-9]{4,8})\b")
_SKIP = {"YOUR", "CODE", "HTTP", "HTML", "DEAR", "WILL", "THAT", "THIS", "WITH", "FROM"}


def _extract_code(text: str) -> str | None:
    text = re.sub(r"<[^>]+>", " ", text)  # strip HTML
    for m in _CODE_RE.finditer(text):
        candidate = m.group(1)
        if candidate not in _SKIP and not candidate.isalpha():
            return candidate
    # fallback: pure numeric 4-8 digits
    m = re.search(r"\b(\d{4,8})\b", text)
    return m.group(1) if m else None

_GUERRILLA_API = "https://api.guerrillamail.com/ajax.php"
_GUERRILLA_UA  = "Mozilla/5.0 (compatible; SoundOnBot/1.0)"

_SWISS_NAMES = [
    "hans", "peter", "urs", "markus", "stefan", "thomas", "michael", "andreas",
    "christian", "daniel", "simon", "lukas", "tobias", "david", "felix",
    "dominik", "marco", "fabian", "reto", "florian", "matthias", "noah",
    "anna", "maria", "sarah", "laura", "julia", "lisa", "nicole", "sandra",
    "monika", "susanne", "barbara", "claudia", "andrea", "sabrina", "nadine",
    "stefanie", "katharina", "franziska", "sophie", "lena", "lea", "hannah",
    "emma", "mia", "sofia", "leonie", "chiara", "valentina", "giulia",
    "jean", "pierre", "marc", "alain", "mathieu", "julien", "nicolas",
]

_SWISS_SURNAMES = [
    "mueller", "meier", "schmid", "keller", "weber", "huber", "steiner",
    "baumann", "moser", "zimmermann", "kunz", "stalder", "frei", "gerber",
    "roth", "brunner", "witmer", "bucher", "maurer", "schenk", "wyss",
    "lehmann", "egger", "bauer", "leuenberger", "rieder", "hauser",
]


class MailTmProvider(IEmailProvider):
    async def create_inbox(self) -> Tuple[str, str]:
        alphabet = string.ascii_lowercase + string.digits
        username = "".join(secrets.choice(alphabet) for _ in range(12))
        email = f"{username}@{_MAILTM_DOMAIN}"
        password = "".join(secrets.choice(alphabet) for _ in range(16))

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{_MAILTM_API}/accounts",
                json={"address": email, "password": password},
            ) as resp:
                resp.raise_for_status()

            async with session.post(
                f"{_MAILTM_API}/token",
                json={"address": email, "password": password},
            ) as resp:
                resp.raise_for_status()
                data = await resp.json()
                token = data["token"]

        return email, token

    async def wait_for_code(self, token: str, timeout: int = 120) -> str:
        headers = {"Authorization": f"Bearer {token}"}
        deadline = asyncio.get_event_loop().time() + timeout

        async with aiohttp.ClientSession(headers=headers) as session:
            while asyncio.get_event_loop().time() < deadline:
                async with session.get(f"{_MAILTM_API}/messages") as resp:
                    resp.raise_for_status()
                    messages = (await resp.json()).get("hydra:member", [])

                for msg in messages:
                    msg_id = msg["id"]
                    async with session.get(f"{_MAILTM_API}/messages/{msg_id}") as resp:
                        resp.raise_for_status()
                        body = (await resp.json()).get("text", "") or ""

                    code = _extract_code(body)
                    if code:
                        return code

                await asyncio.sleep(5)

        raise TimeoutError("Verification code not received within timeout")


class GuerrillaMailProvider(IEmailProvider):
    """Uses Guerrilla Mail public API with realistic Swiss name usernames."""

    async def create_inbox(self) -> Tuple[str, str]:
        # generate a realistic Swiss name username
        first = secrets.choice(_SWISS_NAMES)
        last  = secrets.choice(_SWISS_SURNAMES)
        num   = "".join(secrets.choice(string.digits) for _ in range(2))
        username = f"{first}.{last}{num}"

        async with aiohttp.ClientSession(headers={"User-Agent": _GUERRILLA_UA}) as s:
            # create session first
            async with s.get(f"{_GUERRILLA_API}?f=get_email_address") as resp:
                resp.raise_for_status()
                init = await resp.json(content_type=None)
            token = init["sid_token"]

            # set custom username (domain becomes grr.la)
            async with s.get(
                f"{_GUERRILLA_API}?f=set_email_user&email_user={username}&lang=en&sid_token={token}"
            ) as resp:
                resp.raise_for_status()
                data = await resp.json(content_type=None)

        email = data.get("email_addr") or f"{username}@grr.la"
        return email, token

    async def wait_for_code(self, token: str, timeout: int = 180) -> str:
        deadline = asyncio.get_event_loop().time() + timeout
        seen: set[str] = set()

        async with aiohttp.ClientSession(headers={"User-Agent": _GUERRILLA_UA}) as s:
            while asyncio.get_event_loop().time() < deadline:
                url = f"{_GUERRILLA_API}?f=get_email_list&offset=0&sid_token={token}"
                async with s.get(url) as resp:
                    resp.raise_for_status()
                    data = await resp.json(content_type=None)

                for msg in data.get("list", []):
                    mail_id = str(msg["mail_id"])
                    # check subject first — SoundOn puts code in subject
                    subject = msg.get("mail_subject", "") or ""
                    code = _extract_code(subject)
                    if code:
                        return code

                    if mail_id in seen:
                        continue
                    seen.add(mail_id)

                    async with s.get(
                        f"{_GUERRILLA_API}?f=fetch_email&email_id={mail_id}&sid_token={token}"
                    ) as resp:
                        resp.raise_for_status()
                        detail = await resp.json(content_type=None)

                    body = detail.get("mail_body", "") or ""
                    code = _extract_code(body)
                    if code:
                        return code

                await asyncio.sleep(6)

        raise TimeoutError("Verification code not received within timeout")
