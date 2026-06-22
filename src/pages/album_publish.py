import asyncio
import os
import re
import tempfile
from pathlib import Path

from src.pages.base import BasePage
from src.models.upload_payload import UploadPayload
from src.constants import BASE_URL as _BASE
from src.core.logger import setup_logger

logger = setup_logger("publish")

# Folder artefak debug (screenshot/html) — portabel, bukan path hardcoded.
_ARTIFACTS = Path(tempfile.gettempdir()) / "soundonbot"
_ARTIFACTS.mkdir(parents=True, exist_ok=True)


class AlbumPublishPage(BasePage):
    async def go_to_album_publish(self, url: str = None):
        if url:
            await self.navigate(url)
        else:
            await self.navigate(f"{_BASE}/library/publish/album?lang=id&region=ID")
        await asyncio.sleep(5)
        # We don't need to wait for 'input' explicitly, evaluating scripts later will handle it safely.
            
    async def fill_album_information(self, payload: UploadPayload):
        logger.debug("Waiting for possible ad popups...")
        # SoundOn often shows an ad popup like "Perlu lebih banyak unggahan?". We must wait for it and close it.
        try:
            # Wait up to 6 seconds for the modal to appear
            popup_sel = "button:has-text('Nanti saja'), button:has-text('Not now'), .semi-modal-close, button:has-text('Tutup'), button:has-text('Got it')"
            await self.wait_for_element(popup_sel, timeout=6000)
            logger.debug("Found popup, dismissing it.")
            await self.page.click(popup_sel, force=True)
            await asyncio.sleep(1)
        except Exception:
            logger.debug("No popup found.")
            pass
            
        logger.debug("Dismissing popups (fallback)")
        await self.dismiss_popups()
        await asyncio.sleep(1)
        
        logger.debug("Step 1. Judul Album")
        # 1. Judul Album
        # Find the input using Javascript by looking for the label text
        try:
            input_selector = await self.page.evaluate('''() => {
                const labels = [...document.querySelectorAll('label, span, div')];
                const judulLabel = labels.find(l => l.innerText && (l.innerText.trim() === 'Judul' || l.innerText.toLowerCase().includes('release title')));
                if (judulLabel) {
                    // Try to find an input near it, usually in the same row/group
                    let parent = judulLabel.parentElement;
                    while (parent && parent.tagName !== 'BODY') {
                        const inputs = parent.querySelectorAll('input[type="text"]');
                        if (inputs.length > 0) {
                            // assign a unique ID so playwright can find it easily
                            inputs[0].id = 'soundon-title-input-hack';
                            return '#soundon-title-input-hack';
                        }
                        parent = parent.parentElement;
                    }
                }
                return 'input[type="text"]'; // fallback
            }''')
            
            title_input = self.page.locator(input_selector).first
            await title_input.click()
            await title_input.fill("")
            await title_input.type(payload.title, delay=50)
            await title_input.evaluate('''el => {
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
            }''')
        except Exception as e:
            logger.debug(f"Failed to fill Judul: {e}")
            
        await asyncio.sleep(1)
        
        logger.debug("Step 2. Bahasa Judul")
        # 2. Bahasa Judul
        # SoundOn uses data-formik-id="language" for the container
        await self.page.locator("#language .semi-select").first.click(force=True)
        
        # Try to find a search input specifically related to the select
        search_input = self.page.locator(".semi-select-input input, .semi-popover input[type='text']").first
        if await search_input.count() > 0 and await search_input.is_visible():
            await search_input.fill("English")
            await asyncio.sleep(1)
        else:
            # If no input, just type to search natively
            await self.page.keyboard_type("English")
            await asyncio.sleep(1)
            
        # Select the exact option
        # It could be "English" or "Inggris" depending on the UI language
        await self.page.locator("[class*='option'], [class*='select-option'], [class*='dropdown'] li").filter(has_text=re.compile(r"English|Inggris", re.IGNORECASE)).first.click(force=True)
        
        # 3. Versi dikosongkan (skip)
        
        logger.debug("Step 4. Genre")
        # Genre: click the combobox, then use JS exact match on option text
        await self.page.locator("#mainGenre .semi-select").first.click(force=True)
        await asyncio.sleep(2)
        await self.page.evaluate('''(genre) => {
            const opts = [...document.querySelectorAll("[role='listbox'] .semi-select-option-text")];
            const match = opts.find(el => el.innerText.trim().toLowerCase() === genre.toLowerCase());
            if (match) match.closest("[role='option']").click();
        }''', payload.genre)
        await asyncio.sleep(1)

        # 5. Sub Genre dikosongkan (skip)

        logger.debug("Step 6. Artis Utama")
        # 6. Artis Utama
        await self.page.locator(".artist-list-wYsHYi button").first.click(force=True)
        await asyncio.sleep(2)

        # Dismiss ad popup (appears before artist modal on some accounts)
        await self.page.evaluate('''() => {
            const dialogs = [...document.querySelectorAll("dialog")];
            for (const d of dialogs) {
                if (d.innerHTML.length > 50 && !d.querySelector("#artistRole")) {
                    const closeBtn = d.querySelector("button.so-form-modal-title-close, button[aria-label=\\'close\\']");
                    if (closeBtn) closeBtn.click();
                }
            }
        }''')
        await asyncio.sleep(1)

        # If modal still not open, click tambah again
        if not await self.page.evaluate("() => !!document.getElementById('artistProfile')"):
            await self.page.locator(".artist-list-wYsHYi button").first.click(force=True)
            await asyncio.sleep(2)

        try:
            # Step A: Search artist by name via #artistProfile (SemiUI filterable Select)
            await self.page.evaluate("() => document.getElementById('artistProfile')?.click()")
            await asyncio.sleep(1)
            await self.page.evaluate('''(name) => {
                const inset = document.getElementById("artistProfile")?.querySelector("input");
                if (inset) {
                    inset.focus();
                    const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value").set;
                    setter.call(inset, name);
                    inset.dispatchEvent(new Event("input", {bubbles: true}));
                    inset.dispatchEvent(new Event("change", {bubbles: true}));
                }
            }''', payload.artist)
            await asyncio.sleep(2)

            # Click matching artist option (SoundOn uses class*='target-option', not [role='option'])
            opt_clicked = await self.page.evaluate('''(name) => {
                const opts = [...document.querySelectorAll("[class*='target-option']")];
                const match = opts.find(o => o.getAttribute("artistname")?.toLowerCase() === name.toLowerCase());
                const opt = match || opts[0];
                if (opt) { opt.click(); return opt.getAttribute("artistname") || "clicked"; }
                return "not found";
            }''', payload.artist)
            logger.debug(f"Artist option clicked: {opt_clicked}")
            await asyncio.sleep(1)

            # Step B: Select role via #artistRole
            await self.page.evaluate("() => document.getElementById('artistRole')?.click()")
            await asyncio.sleep(1)
            role_opts = await self.page.evaluate('''() => {
                const lb = document.querySelector("[role='listbox']");
                return lb ? [...lb.querySelectorAll("[role='option']")].map(o => ({id: o.id, text: o.innerText.trim()})) : [];
            }''')
            if role_opts:
                await self.page.locator(f"#{role_opts[0]['id']}").click(force=True, timeout=5000)
                logger.debug(f"Role selected: {role_opts[0]['text']}")
            await asyncio.sleep(1)

            # Step C: Click Kirim inside modal
            kirim_result = await self.page.evaluate('''() => {
                const modal = [...document.querySelectorAll("dialog")].find(d => d.querySelector("#artistRole"));
                if (!modal) return "no modal";
                const btn = [...modal.querySelectorAll("button")].find(b => /kirim|submit/i.test(b.innerText));
                if (btn) { btn.click(); return `clicked: ${btn.innerText.trim()}`; }
                return "kirim not found";
            }''')
            logger.debug(f"Kirim result: {kirim_result}")
            await asyncio.sleep(3)

        except Exception as e:
            logger.debug(f"Error filling Artis Utama: {e}")
        
        # 7. Record Label dikosongkan (skip)
        
        logger.debug("Step 8. Seni Sampul (AI Generator)")
        # 8. Seni Sampul
        try:
            if payload.cover_path:
                logger.debug(f"Uploading cover art directly from {payload.cover_path}")
                cover_input = self.page.locator("input[type='file']").first
                await cover_input.wait_for(state="attached", timeout=10000)
                await cover_input.set_input_files(str(payload.cover_path))
                await asyncio.sleep(4)
                
                # Check if a crop/confirm dialog appears after uploading
                logger.debug("Checking for crop dialog...")
                try:
                    await self.page.locator("button", has_text=re.compile(r"Simpan|Save|Confirm|Apply", re.IGNORECASE)).last.click(timeout=3000)
                    logger.debug("Clicked save on crop dialog.")
                except Exception:
                    logger.debug("No crop dialog found or failed to click.")
                    
                await asyncio.sleep(4) # Tunggu unggah selesai
            else:
                logger.debug("No cover_path provided, skipping cover art.")
        except Exception as e:
            logger.debug(f"Failed to generate/upload cover: {e}")
        
        logger.debug("Step 9. Distribusi lagu sudah pernah dirilis? -> Tidak")
        # 9. Distribusi lagu sudah pernah dirilis? -> Tidak
        try:
            # Cari radio button 'Tidak' di dalam grup tersebut
            tidak_radio = self.page.locator("label", has_text=re.compile(r"Tidak|No", re.IGNORECASE)).first
            await tidak_radio.click(force=True)
        except Exception as e:
            logger.debug(f"Failed to click radio button: {e}")
        
        # 10. UPC dikosongkan (skip)
        
        logger.debug("Step 11. Simpan ke draf saya")
        # 11. Simpan ke draf saya
        await self.page.evaluate('''() => {
            const btns = [...document.querySelectorAll('button')];
            const saveBtn = btns.find(b => b.innerText && (b.innerText.toLowerCase().includes('save to draft') || b.innerText.toLowerCase().includes('simpan ke draf')));
            if(saveBtn) saveBtn.click();
        }''')
        await asyncio.sleep(4)
        
        logger.debug("Step 12. Selanjutnya")
        # 12. Selanjutnya
        await self.page.evaluate('''() => {
            const btns = [...document.querySelectorAll('button')];
            const nextBtn = btns.find(b => b.innerText && (b.innerText.toLowerCase().includes('next') || b.innerText.toLowerCase().includes('selanjutnya')));
            if(nextBtn) nextBtn.click();
        }''')
        await asyncio.sleep(4)
        
        logger.debug("Checking if 'Selanjutnya' worked...")
        try:
            if await self.is_visible("text=kesalahan terdeteksi"):
                logger.debug("'kesalahan terdeteksi' popup appeared! Clicking Perbaiki sekarang...")
                await self.page.locator("button:has-text('Perbaiki sekarang')").first.click(force=True)
                await asyncio.sleep(2)
                logger.debug("Taking screenshot of the actual highlighted error...")
                err_shot = _ARTIFACTS / "debug_actual_error.png"
                await self.page.screenshot(path=str(err_shot), full_page=True)
                raise Exception(f"Validation error occurred on Album Info page. See {err_shot}")
        except Exception as e:
            if "Validation error" in str(e):
                raise
            pass
        
        if not await self.is_visible("text=Track List") and not await self.is_visible("text=Upload") and not await self.is_visible("text=Trek") and not await self.is_visible("text=Unggah") and not await self.is_visible("text=Informasi lagu"):
            err_shot = _ARTIFACTS / "error_album.png"
            await self.screenshot(str(err_shot), full_page=True)
            raise Exception(f"Failed to reach next step after Album Info. Screenshot saved to {err_shot}")

    async def upload_tracks(self, payload: UploadPayload):
        import glob, os
        audio_files = sorted(
            glob.glob(f"{payload.track_path}/*.wav") +
            glob.glob(f"{payload.track_path}/*.mp3") +
            glob.glob(f"{payload.track_path}/*.flac")
        )
        if not audio_files:
            raise Exception("No audio files found")

        track_names = [os.path.splitext(os.path.basename(f))[0] for f in audio_files]
        logger.debug(f"Uploading {len(audio_files)} tracks...")

        # Upload all files first
        for file in audio_files:
            await self.page.upload_file("*:has-text('Tambah Lagu')", file, use_last=True, force=True)
            await asyncio.sleep(4)

        # Fill metadata for each track
        for idx, track_name in enumerate(track_names):
            logger.debug(f"Filling track {idx+1}/{len(track_names)}: {track_name}")

            # Fill title via native setter
            await self.page.evaluate('''([idx, name]) => {
                const mainCards = [...document.querySelectorAll("details.card-oymaL6")]
                    .filter(c => c.querySelector("input[type=text]"));
                const card = mainCards[idx];
                if (!card) return;
                const titleInput = card.querySelector("input[type=text]");
                if (titleInput) {
                    const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value").set;
                    setter.call(titleInput, name);
                    titleInput.dispatchEvent(new Event("input", {bubbles: true}));
                    titleInput.dispatchEvent(new Event("change", {bubbles: true}));
                }
            }''', [idx, track_name])
            await asyncio.sleep(0.5)

            # Click Penulis lagu tambah button
            await self.page.evaluate('''(idx) => {
                const mainCards = [...document.querySelectorAll("details.card-oymaL6")]
                    .filter(c => c.querySelector("input[type=text]"));
                const card = mainCards[idx];
                if (!card) return;
                // Find by label text
                const labelEl = [...card.querySelectorAll("*")]
                    .find(el => el.children.length === 0 && el.innerText?.trim() === "Penulis lagu");
                if (labelEl) {
                    let parent = labelEl.parentElement;
                    while (parent && parent !== card) {
                        const btn = parent.querySelector("button");
                        if (btn && btn.innerText.trim() === "tambah") { btn.click(); return; }
                        parent = parent.parentElement;
                    }
                }
                // Fallback: 5th tambah button in card
                const tambahs = [...card.querySelectorAll("button")]
                    .filter(b => b.innerText.trim() === "tambah");
                if (tambahs.length > 4) tambahs[4].click();
            }''', idx)
            await asyncio.sleep(2)

            # Handle penulis lagu modal (same pattern as artis utama)
            if await self.page.evaluate("() => !!document.getElementById('artistProfile')"):
                await self.page.evaluate("() => document.getElementById('artistProfile')?.click()")
                await asyncio.sleep(1)
                await self.page.evaluate('''(name) => {
                    const inset = document.getElementById("artistProfile")?.querySelector("input");
                    if (inset) {
                        inset.focus();
                        const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value").set;
                        setter.call(inset, name);
                        inset.dispatchEvent(new Event("input", {bubbles: true}));
                        inset.dispatchEvent(new Event("change", {bubbles: true}));
                    }
                }''', payload.artist)
                await asyncio.sleep(3)

                opt = await self.page.evaluate('''(name) => {
                    const opts = [...document.querySelectorAll("[class*='target-option']")];
                    const match = opts.find(o => o.getAttribute("artistname")?.toLowerCase() === name.toLowerCase());
                    const opt = match || opts[0];
                    if (opt) { opt.click(); return opt.getAttribute("artistname") || "clicked"; }
                    return "not found";
                }''', payload.artist)
                logger.debug(f"Songwriter option: {opt}")
                await asyncio.sleep(1)

                await self.page.evaluate('''() => {
                    const modal = [...document.querySelectorAll("dialog")]
                        .find(d => d.querySelector("#artistRole"));
                    if (!modal) return;
                    const btn = [...modal.querySelectorAll("button")]
                        .find(b => /kirim|submit/i.test(b.innerText));
                    if (btn) btn.click();
                }''')
                await asyncio.sleep(2)
            else:
                logger.debug(f"No penulis lagu modal for track {idx+1}")

        # Save to draft
        await self.page.evaluate('''() => {
            const btns = [...document.querySelectorAll('button')];
            const saveBtn = btns.find(b =>
                b.innerText?.toLowerCase().includes('save to draft') ||
                b.innerText?.toLowerCase().includes('simpan ke draf')
            );
            if (saveBtn) saveBtn.click();
        }''')
        await asyncio.sleep(5)
