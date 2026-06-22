"""Intercept network saat klik Create an account."""
import asyncio, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from playwright.async_api import async_playwright
from src.core.email_provider import GuerrillaMailProvider

_URL_SIGNUP = "https://www.soundon.global/login/signup"


async def main():
    provider = GuerrillaMailProvider()
    email, token = await provider.create_inbox()
    password = "SoundOn2025!"
    print(f"Email: {email}", flush=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, slow_mo=400)
        page = await browser.new_page()

        # intercept semua responses
        api_calls = []
        async def on_response(response):
            url = response.url
            if "soundon.global" in url and any(x in url for x in ["register", "signup", "create", "account", "passport"]):
                try:
                    body = await response.text()
                except Exception:
                    body = "(err)"
                api_calls.append(f"[{response.status}] {url}\n    {body[:500]}")

        page.on("response", on_response)

        await page.goto(_URL_SIGNUP)
        await page.wait_for_selector("input[name='username']", timeout=15_000)
        await page.fill("input[name='username']", email)
        await page.fill("input[type='password']", password)
        await page.click("button:has-text('Send code')")
        print("Send code clicked", flush=True)

        print("Polling kode...", flush=True)
        code = await provider.wait_for_code(token, timeout=180)
        print(f"Kode: {code}", flush=True)

        await page.wait_for_selector("input[placeholder='Verification code']", timeout=15_000)
        await page.fill("input[placeholder='Verification code']", code)

        await page.evaluate("() => document.querySelectorAll('.semi-checkbox').forEach(el => el.click())")

        # screenshot sebelum submit
        await page.screenshot(path="/tmp/before_submit.png")

        # klik dan tunggu response
        await page.click("button:has-text('Create an account')")
        await asyncio.sleep(8)

        await page.screenshot(path="/tmp/after_submit.png")
        print(f"URL: {page.url}", flush=True)

        print("\n=== API CALLS ===", flush=True)
        for c in api_calls:
            print(c, flush=True)

        # dump semua error text di halaman
        errors = await page.evaluate("""() => {
            return [...document.querySelectorAll('[class*="error"], [class*="Error"], [class*="alert"]')]
                .map(el => el.innerText.trim()).filter(t => t);
        }""")
        if errors:
            print("\n=== ERRORS ON PAGE ===", flush=True)
            for e in errors:
                print(f"  {e}", flush=True)

        await browser.close()


asyncio.run(main())
