import asyncio
from pathlib import Path
from src.core.browser import PlaywrightBrowser
from src.core.account_manager import JsonAccountRepository
from src.models.browser_config import BrowserConfig
from src.pages.album_publish import AlbumPublishPage
from src.pages.login import LoginPage
import os
import glob
import re

async def main():
    config = BrowserConfig(headless=True)
    browser = PlaywrightBrowser(config)
    await browser.launch()
    page = await browser.new_page()
    
    account_repo = JsonAccountRepository(Path("config/accounts.json"))
    target_account = next(a for a in account_repo.get_all() if a.email == "tgobox.jkt.1747@gmail.com")
    
    login_page = LoginPage(page)
    await login_page.login(target_account.email, target_account.password)
    
    draft_url = "https://www.soundon.global/library/publish/album?source=draft&id=7652210850094319632&lang=id"
    await page._page.goto(draft_url, wait_until="domcontentloaded")
    await asyncio.sleep(5)
    
    publish_page = AlbumPublishPage(page)
    try:
        popup_sel = "button:has-text('Nanti saja'), button:has-text('Not now'), .semi-modal-close, button:has-text('Tutup'), button:has-text('Got it')"
        await publish_page.wait_for_element(popup_sel, timeout=6000)
        await publish_page.page.click(popup_sel, force=True)
        await asyncio.sleep(1)
    except Exception:
        pass
        
    await page._page.locator("button, a").filter(has_text="Selanjutnya").last.click(force=True)
    await asyncio.sleep(8)
    
    track_files = sorted(glob.glob("/home/aaa/Downloads/Jane_Eyre_Songs/Fire Stone/*.wav"))
    track_names = [os.path.splitext(os.path.basename(t))[0] for t in track_files]
    
    # Use pure JS to fill everything instantly!
    # We pass the list of track names to the browser
    await page._page.evaluate("""(trackNames) => {
        return new Promise((resolve) => {
            // Find all track headers and click them all open
            let trackHeaders = [...document.querySelectorAll('div')].filter(d => d.innerText && d.innerText.match(/^[0-9]+$/) && d.nextElementSibling);
            
            // Function to fill a single track
            function fillTrack(idx) {
                if (idx >= trackNames.length || idx >= trackHeaders.length) {
                    resolve("Done");
                    return;
                }
                
                // Open it
                trackHeaders[idx].click();
                
                setTimeout(() => {
                    // Find the panel that just opened
                    // It's usually the next sibling or we can just find the newly visible inputs
                    // An easier way: just find ALL text inputs on the page right now.
                    // The first one is Album Title. The next ones are Track titles!
                    // Wait, if we only open ONE track at a time, there are only a few inputs visible!
                    let inputs = [...document.querySelectorAll('input[type="text"]')];
                    // The album title is inputs[0], Album version is inputs[1], etc.
                    // Actually, let's just scope to the expanded track container
                    let panel = document.querySelector('.semi-collapse-panel'); // The only expanded one
                    if(panel) {
                        // 1. Judul
                        let titleInput = panel.querySelector('input[type="text"]');
                        if(titleInput) {
                            let nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                            nativeInputValueSetter.call(titleInput, trackNames[idx]);
                            titleInput.dispatchEvent(new Event('input', { bubbles: true }));
                            titleInput.dispatchEvent(new Event('change', { bubbles: true }));
                        }
                        
                        // 2. Click 'tambah' for Penulis lagu
                        let labels = [...panel.querySelectorAll('*')].filter(e => e.innerText === 'Penulis lagu');
                        if(labels.length > 0) {
                            let btn = labels[0].parentElement.parentElement.querySelector('button');
                            if(btn) btn.click();
                        }
                    }
                    
                    setTimeout(() => {
                        // 3. Fill Penulis lagu (Kurs)
                        if(panel) {
                            let allTextInputs = panel.querySelectorAll('input[type="text"]');
                            if(allTextInputs.length > 1) {
                                let writerInput = allTextInputs[allTextInputs.length - 1]; // The newly added one
                                let nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                                nativeInputValueSetter.call(writerInput, "Kurs");
                                writerInput.dispatchEvent(new Event('input', { bubbles: true }));
                                writerInput.dispatchEvent(new Event('change', { bubbles: true }));
                                
                                // We need to click the dropdown that appears!
                                setTimeout(() => {
                                    let option = [...document.querySelectorAll('[class*="option"], [class*="select-option"]')].find(e => e.innerText.includes('Kurs'));
                                    if(option) option.click();
                                }, 500);
                            }
                            
                            // 4. Click 'English'
                            let selects = panel.querySelectorAll('.semi-select');
                            if(selects.length > 0) {
                                selects[0].click();
                                setTimeout(() => {
                                    let engOption = [...document.querySelectorAll('[class*="option"], [class*="select-option"]')].find(e => e.innerText.includes('English') || e.innerText.includes('Inggris'));
                                    if(engOption) engOption.click();
                                }, 500);
                            }
                            
                            // 5. Click 'Tidak' for explicit/AI
                            let tidaks = [...panel.querySelectorAll('label')].filter(l => l.innerText === 'Tidak');
                            tidaks.forEach(t => t.click());
                        }
                        
                        // Close it
                        setTimeout(() => {
                            trackHeaders[idx].click();
                            setTimeout(() => fillTrack(idx + 1), 1000);
                        }, 1500);
                        
                    }, 1000);
                    
                }, 1000);
            }
            
            fillTrack(0);
        });
    }""", track_names)
    await asyncio.sleep(2)
    
    # Save to draft
    print("Saving to draft...")
    await page._page.evaluate('''() => {
        const btns = [...document.querySelectorAll('button')];
        const saveBtn = btns.find(b => b.innerText && (b.innerText.toLowerCase().includes('save to draft') || b.innerText.toLowerCase().includes('simpan ke draf')));
        if(saveBtn) saveBtn.click();
    }''')
    await asyncio.sleep(5)
    
    await browser.close()

asyncio.run(main())
