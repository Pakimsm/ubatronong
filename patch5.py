import re

with open('src/pages/lagu_publish.py', 'r') as f:
    content = f.read()

def replace_block(content, old, new):
    if old in content:
        return content.replace(old, new)
    else:
        print("COULD NOT FIND BLOCK:\n", old[:100])
    return content

# 1. Fix Kontributor modal
old_cont_modal = """        has_modal = await self.page._page.evaluate("() => !!document.getElementById('artistProfile')")
        if has_modal:
            await self.page._page.evaluate("() => document.getElementById('artistProfile')?.click()")
            await asyncio.sleep(1)
            await self.page._page.evaluate('''(name) => {
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
            await self.page._page.evaluate('''(name) => {
                const opts = [...document.querySelectorAll("[class*='target-option'], [class*='option']")];
                const match = opts.find(o => o.getAttribute("artistname")?.toLowerCase() === name.toLowerCase());
                const opt = match || opts[0];
                if (opt) opt.click();
            }''', payload.artist)
            await asyncio.sleep(1)
            
            await self.page._page.evaluate("() => document.getElementById('artistRole')?.click()")
            await asyncio.sleep(1)
            await self.page._page.evaluate('''() => {
                const opts = [...document.querySelectorAll("[role='listbox'] [role='option']")];
                const vocalOpt = opts.find(o => o.innerText.toLowerCase().includes('vocalist') || o.innerText.toLowerCase().includes('vokalis'));
                if(vocalOpt) vocalOpt.click();
                else if(opts.length > 0) opts[0].click();
            }''')
            await asyncio.sleep(1)
            
            await self.page._page.evaluate('''() => {
                const modal = [...document.querySelectorAll("dialog")].find(d => d.querySelector("#artistRole") || d.querySelector("#artistProfile"));
                if (!modal) return;
                const btn = [...modal.querySelectorAll("button")].find(b => /kirim|submit/i.test(b.innerText));
                if (btn) btn.click();
            }''')
            await asyncio.sleep(2)"""

new_cont_modal = """        has_modal = await self.page._page.evaluate("() => !!document.querySelector('.semi-modal')")
        if has_modal:
            await self.page._page.evaluate('''(name) => {
                const modal = document.querySelector('.semi-modal');
                if(!modal) return;
                const input = modal.querySelector('input[type="text"]');
                if(input) {
                    input.focus();
                    const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value").set;
                    setter.call(input, name);
                    input.dispatchEvent(new Event("input", {bubbles: true}));
                    input.dispatchEvent(new Event("change", {bubbles: true}));
                }
            }''', payload.artist)
            await asyncio.sleep(2)
            await self.page._page.evaluate('''(name) => {
                const opts = [...document.querySelectorAll(".semi-select-option, [class*='option']")];
                const match = opts.find(o => o.innerText && o.innerText.toLowerCase().includes(name.toLowerCase()));
                if (match) match.click();
            }''', payload.artist)
            await asyncio.sleep(1)
            await self.page._page.evaluate('''() => {
                const modal = document.querySelector('.semi-modal');
                if(!modal) return;
                const selects = [...modal.querySelectorAll('.semi-select')];
                if(selects.length > 0) selects[selects.length - 1].click();
            }''')
            await asyncio.sleep(1)
            await self.page._page.evaluate('''() => {
                const opts = [...document.querySelectorAll(".semi-select-option")];
                const vocalOpt = opts.find(o => o.innerText && (o.innerText.toLowerCase().includes('vocalist') || o.innerText.toLowerCase().includes('vokalis')));
                if(vocalOpt) vocalOpt.click();
            }''')
            await asyncio.sleep(1)
            await self.page._page.evaluate('''() => {
                const modal = document.querySelector('.semi-modal');
                if(!modal) return;
                const btns = [...modal.querySelectorAll("button")];
                const btn = btns.find(b => b.innerText && /kirim|submit|simpan|save/i.test(b.innerText));
                if (btn) btn.click();
            }''')
            await asyncio.sleep(2)"""

content = replace_block(content, old_cont_modal, new_cont_modal)

# 2. Fix Produksi modal
old_prod_modal = """        has_prod_modal = await self.page._page.evaluate("() => !!document.getElementById('artistProfile')")
        if has_prod_modal:
            await self.page._page.evaluate("() => document.getElementById('artistProfile')?.click()")
            await asyncio.sleep(1)
            await self.page._page.evaluate('''(name) => {
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
            await self.page._page.evaluate('''(name) => {
                const opts = [...document.querySelectorAll("[class*='target-option'], [class*='option']")];
                const match = opts.find(o => o.getAttribute("artistname")?.toLowerCase() === name.toLowerCase());
                const opt = match || opts[0];
                if (opt) opt.click();
            }''', payload.artist)
            await asyncio.sleep(1)
            
            await self.page._page.evaluate("() => document.getElementById('artistRole')?.click()")
            await asyncio.sleep(1)
            await self.page._page.evaluate('''() => {
                const opts = [...document.querySelectorAll("[role='listbox'] [role='option']")];
                const prodOpt = opts.find(o => o.innerText.toLowerCase().includes('producer') || o.innerText.toLowerCase().includes('produser'));
                if(prodOpt) prodOpt.click();
                else if(opts.length > 0) opts[0].click();
            }''')
            await asyncio.sleep(1)
            
            await self.page._page.evaluate('''() => {
                const modal = [...document.querySelectorAll("dialog")].find(d => d.querySelector("#artistRole") || d.querySelector("#artistProfile"));
                if (!modal) return;
                const btn = [...modal.querySelectorAll("button")].find(b => /kirim|submit/i.test(b.innerText));
                if (btn) btn.click();
            }''')
            await asyncio.sleep(2)"""

new_prod_modal = """        has_prod_modal = await self.page._page.evaluate("() => !!document.querySelector('.semi-modal')")
        if has_prod_modal:
            await self.page._page.evaluate('''(name) => {
                const modal = document.querySelector('.semi-modal');
                if(!modal) return;
                const input = modal.querySelector('input[type="text"]');
                if(input) {
                    input.focus();
                    const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value").set;
                    setter.call(input, name);
                    input.dispatchEvent(new Event("input", {bubbles: true}));
                    input.dispatchEvent(new Event("change", {bubbles: true}));
                }
            }''', payload.artist)
            await asyncio.sleep(2)
            await self.page._page.evaluate('''(name) => {
                const opts = [...document.querySelectorAll(".semi-select-option, [class*='option']")];
                const match = opts.find(o => o.innerText && o.innerText.toLowerCase().includes(name.toLowerCase()));
                if (match) match.click();
            }''', payload.artist)
            await asyncio.sleep(1)
            await self.page._page.evaluate('''() => {
                const modal = document.querySelector('.semi-modal');
                if(!modal) return;
                const selects = [...modal.querySelectorAll('.semi-select')];
                if(selects.length > 0) selects[selects.length - 1].click();
            }''')
            await asyncio.sleep(1)
            await self.page._page.evaluate('''() => {
                const opts = [...document.querySelectorAll(".semi-select-option")];
                const prodOpt = opts.find(o => o.innerText && (o.innerText.toLowerCase().includes('producer') || o.innerText.toLowerCase().includes('produser')));
                if(prodOpt) prodOpt.click();
            }''')
            await asyncio.sleep(1)
            await self.page._page.evaluate('''() => {
                const modal = document.querySelector('.semi-modal');
                if(!modal) return;
                const btns = [...modal.querySelectorAll("button")];
                const btn = btns.find(b => b.innerText && /kirim|submit|simpan|save/i.test(b.innerText));
                if (btn) btn.click();
            }''')
            await asyncio.sleep(2)"""

content = replace_block(content, old_prod_modal, new_prod_modal)

# 3. Fix Songwriter modal
old_sw_modal = """        has_sw_modal = await self.page._page.evaluate("() => !!document.getElementById('artistProfile')")
        if has_sw_modal:
            await self.page._page.evaluate("() => document.getElementById('artistProfile')?.click()")
            await asyncio.sleep(1)
            await self.page._page.evaluate('''(name) => {
                const inset = document.getElementById("artistProfile")?.querySelector("input");
                if (inset) {
                    inset.focus();
                    const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value").set;
                    setter.call(inset, name);
                    inset.dispatchEvent(new Event("input", {bubbles: true}));
                    inset.dispatchEvent(new Event("change", {bubbles: true}));
                }
            }''', payload.songwriter_name)
            await asyncio.sleep(2)
            await self.page._page.evaluate('''(name) => {
                const opts = [...document.querySelectorAll("[class*='target-option'], [class*='option']")];
                const match = opts.find(o => o.getAttribute("artistname")?.toLowerCase() === name.toLowerCase());
                const opt = match || opts[0];
                if (opt) opt.click();
            }''', payload.songwriter_name)
            await asyncio.sleep(1)
            await self.page._page.evaluate('''() => {
                const modal = [...document.querySelectorAll("dialog")].find(d => d.querySelector("#artistRole") || d.querySelector("#artistProfile"));
                if (!modal) return;
                const btn = [...modal.querySelectorAll("button")].find(b => /kirim|submit/i.test(b.innerText));
                if (btn) btn.click();
            }''')
            await asyncio.sleep(2)
        else:"""

new_sw_modal = """        has_sw_modal = await self.page._page.evaluate("() => !!document.querySelector('.semi-modal')")
        if has_sw_modal:
            await self.page._page.evaluate('''(name) => {
                const modal = document.querySelector('.semi-modal');
                if(!modal) return;
                const input = modal.querySelector('input[type="text"]');
                if(input) {
                    input.focus();
                    const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value").set;
                    setter.call(input, name);
                    input.dispatchEvent(new Event("input", {bubbles: true}));
                    input.dispatchEvent(new Event("change", {bubbles: true}));
                }
            }''', payload.songwriter_name)
            await asyncio.sleep(2)
            await self.page._page.evaluate('''(name) => {
                const opts = [...document.querySelectorAll(".semi-select-option, [class*='option']")];
                const match = opts.find(o => o.innerText && o.innerText.toLowerCase().includes(name.toLowerCase()));
                if (match) match.click();
            }''', payload.songwriter_name)
            await asyncio.sleep(1)
            await self.page._page.evaluate('''() => {
                const modal = document.querySelector('.semi-modal');
                if(!modal) return;
                const btns = [...modal.querySelectorAll("button")];
                const btn = btns.find(b => b.innerText && /kirim|submit|simpan|save/i.test(b.innerText));
                if (btn) btn.click();
            }''')
            await asyncio.sleep(2)
        else:"""

content = replace_block(content, old_sw_modal, new_sw_modal)

with open('src/pages/lagu_publish.py', 'w') as f:
    f.write(content)
