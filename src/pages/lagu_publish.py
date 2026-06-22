import asyncio
import re
from src.pages.base import BasePage
from src.models.upload_payload import UploadPayload
from src.tasks._base import _BASE

class LaguPublishPage(BasePage):
    async def fill_modal_role_profile(self, parent_id: str, name: str):
        try:
            print(f"Filling {parent_id} inside modal with name: {name}...")
            # Click tambah button
            await self.page._page.locator(f"#{parent_id} button").filter(has_text=None or "tambah" or "add").first.click()
            await asyncio.sleep(2)
            
            # Wait for modal dialog - use the legacy show class which is unique to the open dialog
            dialog_loc = self.page._page.locator(".so-form-modal-dialog-legacy-show")
            await dialog_loc.wait_for(state="visible", timeout=10000)
            
            # Click the select wrapper for artistProfile inside the dialog
            select_loc = dialog_loc.locator("#artistProfile")
            await select_loc.click()
            await asyncio.sleep(1.5)
            
            # Fill/type the name into the input element using JS setter to guarantee event binding
            await self.page._page.evaluate('''(name) => {
                const dialog = document.querySelector(".so-form-modal-dialog-legacy-show");
                const select = dialog.querySelector("#artistProfile");
                const input = select.querySelector("input");
                if (input) {
                    input.focus();
                    const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value").set;
                    setter.call(input, name);
                    input.dispatchEvent(new Event("input", {bubbles: true}));
                    input.dispatchEvent(new Event("change", {bubbles: true}));
                }
            }''', name)
            await asyncio.sleep(2)
            
            # Click option in visible portal using dispatched MouseEvents (mousedown, mouseup, click)
            await self.page._page.evaluate('''(name) => {
                const options = [...document.querySelectorAll(`[artistname="${name}"], [inputvalue="${name}"], [class*="target-option"]`)];
                const visibleOpt = options.find(el => el.getBoundingClientRect().height > 0);
                if (visibleOpt) {
                    const isSelected = visibleOpt.classList.contains("selected-GUyiFa") || visibleOpt.className.toLowerCase().includes("selected");
                    if (isSelected) {
                        console.log("Option " + name + " is already selected. Skipping click.");
                    } else {
                        visibleOpt.dispatchEvent(new MouseEvent("mousedown", {bubbles: true}));
                        visibleOpt.dispatchEvent(new MouseEvent("mouseup", {bubbles: true}));
                        visibleOpt.click();
                        console.log("Clicked matching visible option: " + name);
                    }
                } else {
                    console.log("Warning: Could not find visible option for: " + name);
                }
            }''', name)
            await asyncio.sleep(1.5)
            
            # Click submit (Kirim) button
            submit_btn = dialog_loc.locator("button").filter(has_text=re.compile(r"Kirim|Submit|Simpan|Save", re.IGNORECASE)).first
            await submit_btn.click()
            await asyncio.sleep(3)
        except Exception as e:
            print(f"DEBUG: Failed filling {parent_id}: {e}")

    async def fill_modal_contributor_or_production(self, parent_id: str, name: str, role_keyword: str):
        try:
            print(f"Checking/Filling {parent_id} with name '{name}' and role '{role_keyword}'...")
            div_loc = self.page._page.locator(f"#{parent_id}")
            div_text = await div_loc.inner_text()
            if name.lower() in div_text.lower():
                print(f"Value '{name}' is already present in {parent_id}. Skipping.")
                return
                
            await self.page._page.locator(f"#{parent_id} button").filter(has_text=None or "tambah" or "add").first.click()
            await asyncio.sleep(2)
            
            dialog_loc = self.page._page.locator(".so-form-modal-dialog-legacy-show")
            await dialog_loc.wait_for(state="visible", timeout=10000)
            
            # 1. Fill Artist Profile
            select_loc = dialog_loc.locator("#artistProfile")
            await select_loc.click()
            await asyncio.sleep(1.5)
            
            await self.page._page.evaluate('''(name) => {
                const dialog = document.querySelector(".so-form-modal-dialog-legacy-show");
                const select = dialog.querySelector("#artistProfile");
                const input = select.querySelector("input");
                if (input) {
                    input.focus();
                    const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value").set;
                    setter.call(input, name);
                    input.dispatchEvent(new Event("input", {bubbles: true}));
                    input.dispatchEvent(new Event("change", {bubbles: true}));
                }
            }''', name)
            await asyncio.sleep(2)
            
            await self.page._page.evaluate('''(name) => {
                const options = [...document.querySelectorAll(`[artistname="${name}"], [inputvalue="${name}"], [class*="target-option"]`)];
                const visibleOpt = options.find(el => el.getBoundingClientRect().height > 0);
                if (visibleOpt) {
                    visibleOpt.dispatchEvent(new MouseEvent("mousedown", {bubbles: true}));
                    visibleOpt.dispatchEvent(new MouseEvent("mouseup", {bubbles: true}));
                    visibleOpt.click();
                }
            }''', name)
            await asyncio.sleep(1.5)
            
            # 2. Fill Role
            await self.page._page.evaluate('''() => {
                const dialog = document.querySelector(".so-form-modal-dialog-legacy-show");
                const selects = [...dialog.querySelectorAll(".semi-select")];
                const roleSelect = selects.find(s => s.id !== "artistProfile");
                if (roleSelect) roleSelect.click();
            }''')
            await asyncio.sleep(1.5)
            
            await self.page._page.evaluate('''(role) => {
                const opts = [...document.querySelectorAll(".semi-select-option")];
                const match = opts.find(o => o.innerText && o.innerText.toLowerCase().includes(role.toLowerCase()) && o.getBoundingClientRect().height > 0);
                if (match) {
                    match.dispatchEvent(new MouseEvent("mousedown", {bubbles: true}));
                    match.dispatchEvent(new MouseEvent("mouseup", {bubbles: true}));
                    match.click();
                }
            }''', role_keyword)
            await asyncio.sleep(1.5)
            
            # Click Kirim
            submit_btn = dialog_loc.locator("button").filter(has_text=re.compile(r"Kirim|Submit|Simpan|Save", re.IGNORECASE)).first
            await submit_btn.click()
            await asyncio.sleep(3)
        except Exception as e:
            print(f"DEBUG: Failed filling contributor/production {parent_id}: {e}")

    async def fill_select_field(self, label_text: str, search_keyword: str) -> None:
        try:
            print(f"Filling select field '{label_text}' with keyword '{search_keyword}'...")
            await self.page._page.evaluate('''([lbl]) => {
                const divs = [...document.querySelectorAll("div")];
                const field = divs.find(d => d.innerText && d.innerText.includes(lbl) && d.querySelector(".semi-select"));
                if (field) {
                    const select = field.querySelector(".semi-select");
                    if (select) select.click();
                }
            }''', [label_text])
            await asyncio.sleep(1.5)
            
            await self.page._page.evaluate('''([kw]) => {
                const options = [...document.querySelectorAll(".semi-select-option, [role='option'], [class*='option']")];
                const match = options.find(o => o.innerText && o.innerText.toLowerCase().includes(kw.toLowerCase()) && o.getBoundingClientRect().height > 0);
                if (match) {
                    match.dispatchEvent(new MouseEvent("mousedown", {bubbles: true}));
                    match.dispatchEvent(new MouseEvent("mouseup", {bubbles: true}));
                    match.click();
                }
            }''', [search_keyword])
            await asyncio.sleep(1.5)
        except Exception as e:
            print(f"DEBUG: Failed to fill select field '{label_text}': {e}")

    async def go_to_single_publish(self):
        await self.navigate(f"{_BASE}/library/publish/single?lang=id&region=ID")
        await asyncio.sleep(5)
        
        # Discard draft / quote popup checks
        for _ in range(5):
            await self.dismiss_popups()
            
            # Check for resume draft dialog (clicking Start New Release if present)
            try:
                start_new_sel = "button:has-text('Mulai rilis baru'), button:has-text('Start new release')"
                if await self.is_visible(start_new_sel):
                    print("Clicking Start New Release...")
                    await self.click(start_new_sel, timeout=3000)
                    await asyncio.sleep(3)
            except:
                pass

        if await self.is_visible("text=Single Song") or await self.is_visible("text=Choose your release type") or await self.is_visible("text=Lagu Tunggal"):
            try:
                await self.page._page.locator("div.card-y6wAye").filter(has_text=re.compile(r"Single Song|Lagu Tunggal", re.IGNORECASE)).first.click(force=True)
                await asyncio.sleep(3)
            except:
                pass
                
        # One more dismiss check
        await self.dismiss_popups()
                
        try:
            await self.page._page.wait_for_selector("input[type='file'][accept*='.mp3']", state="attached", timeout=15000)
        except Exception:
            html = await self.page._page.content()
            with open("/home/aaa/soundonbot/debug_track_fail.html", "w", encoding="utf-8") as f:
                f.write(html)
            raise Exception("Failed to reach Track Information step. Page might be loading too slow or ad blocker issue. Check debug_track_fail.html")
        
    async def fill_track_information(self, payload: UploadPayload):
        await self.dismiss_popups()
        await self.page.set_input_files("input[type='file'][accept*='.mp3']", str(payload.track_path))
        await self.dismiss_popups()
        
        # Wait for audio upload to finish (when 'Upload complete' is visible) BEFORE filling the form
        try:
            await self.page._page.wait_for_selector("text='Upload complete'", state="visible", timeout=1800000)
            await asyncio.sleep(2)
        except Exception as e:
            print(f"DEBUG: Audio upload wait failed: {e}")

        await self.dismiss_popups()
        
        try:
            input_selector = await self.page._page.evaluate('''() => {
                const labels = [...document.querySelectorAll('label, span, div')];
                const judulLabel = labels.find(l => l.innerText && (l.innerText.trim() === 'Judul' || l.innerText.toLowerCase().includes('release title') || l.innerText.toLowerCase().includes('track title')));
                if (judulLabel) {
                    let parent = judulLabel.parentElement;
                    while (parent && parent.tagName !== 'BODY') {
                        const inputs = parent.querySelectorAll('input[type="text"]');
                        if (inputs.length > 0) {
                            inputs[0].id = 'soundon-title-input-hack';
                            return '#soundon-title-input-hack';
                        }
                        parent = parent.parentElement;
                    }
                }
                return 'input[type="text"]'; // fallback
            }''')
            title_input = self.page._page.locator(input_selector).first
            await title_input.click(force=True)
            await title_input.fill("")
            await title_input.type(payload.title, delay=50)
        except:
            await self.fill_react("input[type='text']", payload.title)
        await asyncio.sleep(2)

        # Title Language (Bahasa judul)
        try:
            await self.fill_select_field("Bahasa judul", "indonesia")
        except Exception as e:
            print(f"DEBUG: Failed Bahasa judul: {e}")
        await asyncio.sleep(1)

        # Instrumental
        try:
            await self.click_radio_option("Instrumental", "Tidak")
        except Exception as e:
            print(f"DEBUG: Failed Instrumental: {e}")
        await asyncio.sleep(1)

        # Primary Artist (mainArtists)
        try:
            print("Clicking tambah button for mainArtists...")
            await self.page._page.evaluate('''() => {
                const mainArtistsDiv = document.getElementById("mainArtists");
                if (mainArtistsDiv) {
                    const btn = mainArtistsDiv.querySelector("button");
                    if (btn) btn.click();
                }
            }''')
            await asyncio.sleep(2)

            print("Opening #artistProfile select...")
            await self.page.click("#artistProfile")
            await asyncio.sleep(1)

            print(f"Typing '{payload.artist}' into #artistProfile input...")
            await self.page._page.evaluate('''(name) => {
                const container = document.getElementById("artistProfile");
                if (!container) return;
                const input = container.querySelector("input");
                if (input) {
                    input.focus();
                    const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value").set;
                    setter.call(input, name);
                    input.dispatchEvent(new Event("input", {bubbles: true}));
                    input.dispatchEvent(new Event("change", {bubbles: true}));
                }
            }''', payload.artist)
            await asyncio.sleep(2)

            print("Selecting the matching option...")
            await self.page._page.evaluate('''(name) => {
                const options = [...document.querySelectorAll("[class*='target-option']")];
                const match = options.find(o => o.getAttribute("artistname")?.toLowerCase() === name.toLowerCase());
                const opt = match || options[0];
                if (opt) opt.click();
            }''', payload.artist)
            await asyncio.sleep(1)

            print("Submitting the modal...")
            await self.page._page.evaluate('''() => {
                const modal = document.querySelector(".so-form-modal");
                if (!modal) return;
                const buttons = [...modal.querySelectorAll("button")];
                const kirim = buttons.find(b => b.innerText && /kirim|submit|simpan|save/i.test(b.innerText));
                if (kirim) kirim.click();
            }''')
            await asyncio.sleep(2)
        except Exception as e:
            print(f"DEBUG: Failed to select primary artist: {e}")

        # Contributor Vokalis
        try:
            await self.fill_modal_contributor_or_production("contributors", payload.artist, "vokalis")
        except Exception as e:
            print(f"DEBUG: Failed Contributor: {e}")
        await asyncio.sleep(1)

        # Production Role Produser
        try:
            await self.fill_modal_contributor_or_production("productionAndEngineering", payload.artist, "produser")
        except Exception as e:
            print(f"DEBUG: Failed Production Role: {e}")
        await asyncio.sleep(1)

        # Fill Songwriter (Penulis lagu)
        await self.fill_modal_role_profile("composers", payload.songwriter_name)
        await asyncio.sleep(1)

        # Fill Lyricist (Penulis lirik)
        await self.fill_modal_role_profile("lyricists", payload.songwriter_name)
        await asyncio.sleep(1)

        # Licensed content (konten berlisensi)
        try:
            await self.click_radio_option("berlisensi", "Tidak")
        except Exception as e:
            print(f"DEBUG: Failed Konten Berlisensi: {e}")
        await asyncio.sleep(1)

        # Genre
        await self.page._page.evaluate('''() => {
            const select = document.querySelector("#mainGenre .semi-select");
            if(select) select.click();
            else {
                const btns = [...document.querySelectorAll('button')];
                const genreBtn = btns.find(b => (b.innerText.trim().toLowerCase() === 'add' || b.innerText.trim().toLowerCase() === 'tambah') && 
                    b.closest('div').innerText.includes('Genre'));
                if(genreBtn) genreBtn.click();
            }
        }''')
        await asyncio.sleep(2)
        await self.page._page.evaluate('''(genre) => {
            const opts = [...document.querySelectorAll("[role='listbox'] .semi-select-option-text, [role='listbox'] li")];
            const match = opts.find(el => el.innerText.trim().toLowerCase() === genre.toLowerCase() && el.getBoundingClientRect().width > 0);
            if (match) match.closest("[role='option'], li").click();
            else {
                const fallback = opts.find(el => el.getBoundingClientRect().width > 0);
                if (fallback) fallback.closest("[role='option'], li").click();
            }
        }''', payload.genre)
        await asyncio.sleep(1)

        # Fill Lyrics Language (Bahasa lirik)
        try:
            await self.fill_select_field("Bahasa lirik", "indonesia")
        except Exception as e:
            print(f"DEBUG: Failed Bahasa lirik: {e}")
        await asyncio.sleep(1)

        # Fill Explicit (Eksplisit)
        try:
            await self.click_radio_option("Eksplisit", "Tidak")
        except Exception as e:
            print(f"DEBUG: Failed Explicit: {e}")
        await asyncio.sleep(1)

        # Already released (Sudah pernah dirilis?)
        try:
            await self.click_radio_option("pernah dirilis", "Tidak")
        except Exception as e:
            print(f"DEBUG: Failed Pernah Dirilis: {e}")
        await asyncio.sleep(1)

        await self.page._page.screenshot(path="/home/aaa/soundonbot/debug_before_cover.png", full_page=True)
        try:
            cover_path = "/home/aaa/soundonbot/generated_cover.jpg"
            # Generate a solid color cover with PIL
            from PIL import Image, ImageDraw, ImageFont
            img = Image.new('RGB', (3000, 3000), color = (73, 109, 137))
            d = ImageDraw.Draw(img)
            # Try to get a basic font, fallback to default
            try:
                fnt = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 150)
            except:
                fnt = ImageFont.load_default()
            d.text((1500, 1500), payload.title, font=fnt, fill=(255, 255, 0), anchor="mm")
            d.text((1500, 1800), payload.artist, font=fnt, fill=(255, 255, 255), anchor="mm")
            img.save(cover_path)
            
            print("Waiting for cover upload input...")
            image_selector = "input[type='file'][accept*='.jpg'], input[type='file'][accept*='.jpeg'], input[type='file'][accept*='.png']"
            await self.page._page.wait_for_selector(image_selector, state="attached", timeout=30000)
            
            print("Uploading cover image...")
            await self.page.set_input_files(image_selector, cover_path)
            # Wait for upload to complete
            await asyncio.sleep(10)
        except Exception as e:
            print(f"DEBUG: Cover upload failed: {e}")
            

        await self.page._page.evaluate('''() => {
            const btns = [...document.querySelectorAll('button, div, span, a')];
            const btn = btns.find(b => b.innerText && (b.innerText.trim() === 'Next' || b.innerText.trim() === 'Selanjutnya') && b.getBoundingClientRect().width > 0);
            if (btn) btn.click();
        }''')
        await asyncio.sleep(2)
        await self.dismiss_validation_modal()
        
    async def fill_release_settings(self, payload: UploadPayload):
        try:
            print("Selecting 'Lewati untuk sekarang' for TikTok Prerilis...")
            await self.click_radio_option("Prarilis TikTok", "Lewati untuk sekarang")
        except Exception as e:
            print(f"DEBUG: Failed TikTok Prerilis selection: {e}")
        await asyncio.sleep(1)
        
        await self.page._page.evaluate('''() => {
            const btns = [...document.querySelectorAll('button, div, span, a')];
            const btn = btns.find(b => b.innerText && (b.innerText.trim() === 'Next' || b.innerText.trim() === 'Selanjutnya') && b.getBoundingClientRect().width > 0);
            if (btn) btn.click();
        }''')
        await asyncio.sleep(2)
        await self.dismiss_validation_modal()

    async def skip_more_options(self):
        try:
            print("Selecting 100% publishing rights...")
            await self.click_radio_option("Hak penerbitan", "100%")
        except Exception as e:
            print(f"DEBUG: Error handling publishing rights: {e}")
        await asyncio.sleep(1.5)

        await self.page._page.evaluate('''() => {
            const btns = [...document.querySelectorAll('button, div, span, a')];
            const btn = btns.find(b => b.innerText && (b.innerText.trim() === 'Next' || b.innerText.trim() === 'Selanjutnya') && b.getBoundingClientRect().width > 0);
            if (btn) btn.click();
        }''')
        await asyncio.sleep(2)
        await self.dismiss_validation_modal()
        
    async def dismiss_validation_modal(self) -> bool:
        try:
            dismissed = await self.page._page.evaluate('''() => {
                const modal = document.querySelector('.semi-modal');
                if (modal && modal.innerText && (modal.innerText.includes('kesalahan terdeteksi') || modal.innerText.includes('errors detected'))) {
                    const btns = [...modal.querySelectorAll('button, span, div')];
                    const nantiBtn = btns.find(b => b.innerText && (b.innerText.trim() === 'Nanti' || b.innerText.trim() === 'Later'));
                    if (nantiBtn) {
                        nantiBtn.click();
                        return true;
                    }
                }
                return false;
            }''')
            if dismissed:
                print("Dismissed validation modal (clicked Nanti).")
                await asyncio.sleep(1.5)
                return True
        except Exception as e:
            print(f"DEBUG: Error dismissing validation modal: {e}")
        return False

    async def submit(self) -> bool:
        await self.dismiss_validation_modal()
        # Submit to draft
        await self.page._page.evaluate('''() => {
            const btns = [...document.querySelectorAll('button, .semi-button, [role="button"]')];
            const btn = btns.find(b => (b.innerText.toLowerCase().includes('simpan ke draf') || b.innerText.toLowerCase().includes('save to draft')) && b.getBoundingClientRect().width > 0);
            if (btn) btn.click();
        }''')
        await asyncio.sleep(2.5)
        # Dismiss any validation modal that pops up after clicking save
        await self.dismiss_validation_modal()
        
        try:
            await self.page._page.wait_for_url("**/list?type=drafts*", timeout=15000)
            await asyncio.sleep(2)
        except Exception:
            await asyncio.sleep(5)
            
        return True
