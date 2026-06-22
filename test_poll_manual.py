"""Poll Guerrilla Mail dan juga coba send fresh code, tunggu 5 menit."""
import asyncio, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from playwright.async_api import async_playwright
from src.core.email_provider import GuerrillaMailProvider

_URL_SIGNUP = "https://www.soundon.global/login/signup"


async def main():
    provider = GuerrillaMailProvider()
    email, token = await provider.create_inbox()
    print(f"Email: {email}", flush=True)
    print(f"Token: {token[:20]}...", flush=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, slow_mo=300)
        page = await browser.new_page()
        await page.goto(_URL_SIGNUP)
        await page.wait_for_selector("input[name='username']", timeout=15_000)
        await page.fill("input[name='username']", email)
        await page.fill("input[type='password']", "SoundOn2025!")
        await page.click("button:has-text('Send code')")
        await asyncio.sleep(3)
        # ambil email_ticket dari API response jika ada
        print("Send code clicked, menunggu email...", flush=True)
        await browser.close()

    # Poll 5 menit
    import aiohttp, re
    _API = "https://api.guerrillamail.com/ajax.php"
    _UA  = "Mozilla/5.0"
    seen = set()
    deadline = asyncio.get_event_loop().time() + 300

    async with aiohttp.ClientSession(headers={"User-Agent": _UA}) as s:
        i = 0
        while asyncio.get_event_loop().time() < deadline:
            i += 1
            url = f"{_API}?f=get_email_list&offset=0&sid_token={token}"
            async with s.get(url) as resp:
                data = await resp.json(content_type=None)
            msgs = data.get("list", [])
            print(f"[poll {i}] {len(msgs)} pesan di inbox", flush=True)
            for msg in msgs:
                mail_id = str(msg["mail_id"])
                print(f"  msg_id={mail_id} subj={msg.get('mail_subject','')}", flush=True)
                if mail_id not in seen:
                    seen.add(mail_id)
                    async with s.get(f"{_API}?f=fetch_email&email_id={mail_id}&sid_token={token}") as r2:
                        detail = await r2.json(content_type=None)
                    body = re.sub(r"<[^>]+>", " ", detail.get("mail_body", "") or "")
                    print(f"  body snippet: {body[:200]}", flush=True)
                    m = re.search(r"\b(\d{4,8})\b", body)
                    if m:
                        print(f"KODE DITEMUKAN: {m.group(1)}", flush=True)
                        return
            await asyncio.sleep(10)

    print("Timeout 5 menit — email tidak diterima.", flush=True)


asyncio.run(main())
