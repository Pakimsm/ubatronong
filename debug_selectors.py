"""
Debug: handle ad popup, open artist modal, fill name, select role, click Kirim.
"""
import asyncio
import json
from pathlib import Path
from src.core.browser import PlaywrightBrowser
from src.core.account_manager import JsonAccountRepository
from src.models.browser_config import BrowserConfig
from src.tasks._base import _BASE
import re

async def main():
    config = BrowserConfig(headless=False)
    browser = PlaywrightBrowser(config)
    account_repo = JsonAccountRepository(Path("config/accounts.json"))

    accounts = account_repo.get_active()
    account = next((a for a in accounts if "tgobox" in a.email), accounts[0])
    await browser.launch()
    page = await browser.new_page()

    from src.pages.login import LoginPage
    login = LoginPage(page)
    await login.login(account.email, account.password)
    await asyncio.sleep(3)

    await page._page.goto(f"{_BASE}/library/publish/album?lang=id&region=ID")
    await asyncio.sleep(5)

    # ── Dismiss page-level popup ───────────────────────────────────────────
    try:
        await page._page.click("button:has-text('Nanti saja'), button:has-text('Not now')", force=True, timeout=5000)
        await asyncio.sleep(1)
    except Exception:
        pass

    # ── Click tambah button ─────────────────────────────────────────────────
    print("=== Clicking tambah artist button ===")
    await page._page.locator(".artist-list-wYsHYi button").first.click(force=True)
    await asyncio.sleep(2)

    # ── Dismiss ad popup that may appear ──────────────────────────────────
    print("Dismissing any ad popups...")
    for _ in range(3):
        dismissed = await page._page.evaluate('''() => {
            // Close any dialog that does NOT contain #artistRole
            const dialogs = [...document.querySelectorAll("dialog")];
            for (const d of dialogs) {
                if (d.innerHTML.length > 50 && !d.querySelector("#artistRole")) {
                    // Find close button inside
                    const closeBtn = d.querySelector("button[aria-label='close'], .semi-modal-close, button.so-form-modal-title-close");
                    if (closeBtn) { closeBtn.click(); return "dismissed via close btn"; }
                }
            }
            // Also try Nanti saja
            const nanti = [...document.querySelectorAll("button")].find(b => b.innerText.includes("Nanti") || b.innerText.includes("Not now") || b.innerText.includes("Tutup"));
            if (nanti) { nanti.click(); return "dismissed via nanti"; }
            return null;
        }''')
        if dismissed:
            print(f"  Dismissed popup: {dismissed}")
            await asyncio.sleep(1)
        else:
            break

    await asyncio.sleep(1)

    # ── Check if artist modal is open ─────────────────────────────────────
    artist_modal_open = await page._page.evaluate("() => !!document.getElementById('artistRole')")
    print(f"Artist modal open: {artist_modal_open}")

    if not artist_modal_open:
        print("Artist modal not open, clicking tambah again...")
        await page._page.locator(".artist-list-wYsHYi button").first.click(force=True)
        await asyncio.sleep(2)
        artist_modal_open = await page._page.evaluate("() => !!document.getElementById('artistRole')")
        print(f"Artist modal open after second click: {artist_modal_open}")

    if not artist_modal_open:
        print("ERROR: Cannot open artist modal!")
        await page._page.screenshot(path="debug_no_modal.png")
        await browser.close()
        return

    # Dump modal HTML
    modal_html = await page._page.evaluate('''() => {
        const dialogs = [...document.querySelectorAll("dialog")];
        const active = dialogs.find(d => d.querySelector("#artistRole"));
        return active ? active.innerHTML.substring(0, 4000) : "not found";
    }''')
    with open("debug_modal_artist.html", "w") as f:
        f.write(modal_html)
    print(f"Modal HTML ({len(modal_html)} chars) saved")

    await page._page.screenshot(path="debug_artist_modal.png")

    # ── Fill artist name ───────────────────────────────────────────────────
    print("\n=== Finding artist name input ===")
    inputs_info = await page._page.evaluate('''() => {
        const modal = [...document.querySelectorAll("dialog")].find(d => d.querySelector("#artistRole"));
        if (!modal) return [];
        return [...modal.querySelectorAll("input")].map(el => ({
            id: el.id, type: el.type, placeholder: el.placeholder,
            value: el.value, class: el.className.substring(0,60), name: el.name
        }));
    }''')
    print("Modal inputs:", json.dumps(inputs_info, indent=2))

    # Find the search/name input - it should be type=text with placeholder related to artist
    artist_input = page._page.locator("dialog:has(#artistRole) input[type='text']").first
    artist_input_count = await page._page.locator("dialog:has(#artistRole) input[type='text']").count()
    print(f"text inputs in artist dialog: {artist_input_count}")

    if artist_input_count > 0:
        await artist_input.scroll_into_view_if_needed()
        await artist_input.click(force=True)
        await asyncio.sleep(0.5)
        await artist_input.fill("Kurs")
        await asyncio.sleep(2)
        print("Typed 'Kurs'")
        await page._page.screenshot(path="debug_typed_kurs.png")

        # Check autocomplete
        ac = await page._page.evaluate('''() => {
            const lb = document.querySelector("[role='listbox']");
            return lb ? [...lb.querySelectorAll("[role='option']")].map(o => o.innerText.trim()) : [];
        }''')
        print(f"Autocomplete options: {ac}")

        if ac:
            # Click matching
            matched = next((o for o in ac if "kurs" in o.lower()), None)
            if matched:
                await page._page.locator("[role='listbox'] [role='option']").filter(has_text=matched).first.click(force=True)
                print(f"Clicked option: {matched}")
            else:
                await page._page.locator("[role='listbox'] [role='option']").first.click(force=True)
                print(f"Clicked first option: {ac[0]}")
            await asyncio.sleep(1)
    else:
        print("No text input found in modal - checking if artist search works differently")

    # ── Select role "Artis utama" ──────────────────────────────────────────
    print("\n=== Selecting role ===")
    await page._page.evaluate("() => document.getElementById('artistRole')?.click()")
    await asyncio.sleep(1)

    role_opts = await page._page.evaluate('''() => {
        const lb = document.querySelector("[role='listbox']");
        return lb ? [...lb.querySelectorAll("[role='option']")].map(o => ({id: o.id, text: o.innerText.trim()})) : [];
    }''')
    print(f"Role options: {role_opts}")

    if role_opts:
        await page._page.locator(f"#{role_opts[0]['id']}").click(force=True, timeout=5000)
        print(f"Selected role: {role_opts[0]['text']}")
        await asyncio.sleep(1)

    state = await page._page.evaluate('''() => {
        const cb = document.getElementById("artistRole");
        return {
            selected: cb?.querySelector(".semi-select-selection-text:not(.semi-select-selection-placeholder)")?.innerText?.trim(),
            is_placeholder: !!cb?.querySelector(".semi-select-selection-placeholder")
        };
    }''')
    print("Role state:", state)

    await page._page.screenshot(path="debug_before_kirim.png")

    # ── Click Kirim ────────────────────────────────────────────────────────
    print("\n=== Clicking Kirim ===")
    # Look inside the active modal
    kirim_clicked = await page._page.evaluate('''() => {
        const modal = [...document.querySelectorAll("dialog")].find(d => d.querySelector("#artistRole"));
        if (!modal) return "no modal";
        const btn = [...modal.querySelectorAll("button")].find(b =>
            /kirim|submit|confirm/i.test(b.innerText)
        );
        if (btn) { btn.click(); return `clicked: ${btn.innerText.trim()}`; }
        // try footer buttons
        const allBtns = [...modal.querySelectorAll("button")].map(b => b.innerText.trim());
        return `not found, buttons: ${JSON.stringify(allBtns)}`;
    }''')
    print(f"Kirim result: {kirim_clicked}")
    await asyncio.sleep(3)

    await page._page.screenshot(path="debug_after_kirim.png")
    after = await page._page.evaluate('''() => ({
        modal_open: !!document.getElementById("artistRole"),
        errors: [...document.querySelectorAll(".semi-form-field-error-message, [class*='error-msg']")].map(e => e.innerText.trim()).filter(Boolean),
        artist_tags: [...document.querySelectorAll(".artist-list-wYsHYi")].map(el => el.innerText.trim().substring(0, 100))
    })''')
    print("After Kirim:", json.dumps(after, indent=2))

    await browser.close()
    print("\nDone.")

if __name__ == "__main__":
    asyncio.run(main())
