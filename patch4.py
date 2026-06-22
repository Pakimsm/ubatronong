import re

with open('src/pages/lagu_publish.py', 'r') as f:
    content = f.read()

def replace_block(content, old, new):
    if old in content:
        return content.replace(old, new)
    return content

# Fix audio wait
old_audio = """        try:
            await self.page._page.wait_for_selector("text='Upload complete', text='Berhasil'", state="visible", timeout=120000)
            await asyncio.sleep(2)
        except Exception as e:
            print(f"DEBUG: Audio upload wait failed: {e}")"""
new_audio = """        try:
            await self.page._page.wait_for_selector("text=/Upload complete|Berhasil/i", state="visible", timeout=120000)
            await asyncio.sleep(2)
        except Exception as e:
            print(f"DEBUG: Audio upload wait failed: {e}")"""
content = replace_block(content, old_audio, new_audio)

# Fix Bahasa judul
old_bj = """        try:
            field = self.page._page.locator(".semi-form-field").filter(has_text=re.compile(r"Bahasa judul|Title language", re.I)).first
            await field.locator(".semi-select").click(force=True)
            await asyncio.sleep(1)
            await self.page._page.locator(".semi-select-option").filter(has_text=re.compile(r"Indonesia", re.I)).first.click(force=True)
        except Exception as e:
            print(f"DEBUG: Failed Bahasa judul: {e}")
        await asyncio.sleep(1)"""
new_bj = """        try:
            await self.page._page.evaluate('''() => {
                const labels = [...document.querySelectorAll('div, span, label')];
                const target = labels.find(l => l.innerText && (l.innerText.toLowerCase() === 'bahasa judul' || l.innerText.toLowerCase() === 'title language'));
                if (!target) return;
                let p = target.parentElement;
                for (let i = 0; i < 6 && p; i++) {
                    const select = p.querySelector('.semi-select');
                    if (select) { select.click(); return; }
                    p = p.parentElement;
                }
            }''')
            await asyncio.sleep(1)
            await self.page._page.evaluate('''() => {
                const opts = [...document.querySelectorAll('.semi-select-option')];
                const opt = opts.find(o => o.innerText && o.innerText.toLowerCase().includes('indonesia'));
                if (opt) opt.click();
            }''')
        except Exception as e:
            print(f"DEBUG: Failed Bahasa judul: {e}")
        await asyncio.sleep(1)"""
content = replace_block(content, old_bj, new_bj)

# Fix Instrumental
old_inst = """        try:
            field = self.page._page.locator(".semi-form-field").filter(has_text=re.compile(r"Instrumental", re.I)).first
            await field.locator("label").filter(has_text=re.compile(r"^Tidak$|^No$", re.I)).first.click(force=True)
        except Exception as e:
            print(f"DEBUG: Failed Instrumental: {e}")
        await asyncio.sleep(1)"""
new_inst = """        try:
            await self.page._page.evaluate('''() => {
                const labels = [...document.querySelectorAll('div, span, label')];
                const target = labels.find(l => l.innerText && l.innerText.toLowerCase() === 'instrumental');
                if (!target) return;
                let p = target.parentElement;
                for (let i = 0; i < 6 && p; i++) {
                    const radios = [...p.querySelectorAll('label')];
                    const noBtn = radios.find(r => r.innerText && (r.innerText.toLowerCase().trim() === 'tidak' || r.innerText.toLowerCase().trim() === 'no'));
                    if (noBtn) { noBtn.click(); return; }
                    p = p.parentElement;
                }
            }''')
        except Exception as e:
            print(f"DEBUG: Failed Instrumental: {e}")
        await asyncio.sleep(1)"""
content = replace_block(content, old_inst, new_inst)

# Fix Kontributor
old_cont = """        try:
            field = self.page._page.locator(".semi-form-field").filter(has_text=re.compile(r"Contributor|Kontributor", re.I)).first
            await field.locator("button").filter(has_text=re.compile(r"tambah|add", re.I)).click(force=True)
        except Exception as e:
            print(f"DEBUG: Failed Kontributor: {e}")
        await asyncio.sleep(2)"""
new_cont = """        try:
            await self.page._page.evaluate('''() => {
                const labels = [...document.querySelectorAll('div, span, label')];
                const target = labels.find(l => l.innerText && (l.innerText.toLowerCase() === 'kontributor' || l.innerText.toLowerCase() === 'contributor'));
                if (!target) return;
                let p = target.parentElement;
                for (let i = 0; i < 6 && p; i++) {
                    const btns = [...p.querySelectorAll('button')];
                    const addBtn = btns.find(b => b.innerText && (b.innerText.toLowerCase().includes('tambah') || b.innerText.toLowerCase().includes('add')));
                    if (addBtn) { addBtn.click(); return; }
                    p = p.parentElement;
                }
            }''')
        except Exception as e:
            print(f"DEBUG: Failed Kontributor: {e}")
        await asyncio.sleep(2)"""
content = replace_block(content, old_cont, new_cont)

# Fix Produksi
old_prod = """        try:
            field = self.page._page.locator(".semi-form-field").filter(has_text=re.compile(r"produksi|production", re.I)).first
            await field.locator("button").filter(has_text=re.compile(r"tambah|add", re.I)).click(force=True)
        except Exception as e:
            print(f"DEBUG: Failed Produksi: {e}")
        await asyncio.sleep(2)"""
new_prod = """        try:
            await self.page._page.evaluate('''() => {
                const labels = [...document.querySelectorAll('div, span, label')];
                const target = labels.find(l => l.innerText && (l.innerText.toLowerCase().includes('produksi') || l.innerText.toLowerCase().includes('production')));
                if (!target) return;
                let p = target.parentElement;
                for (let i = 0; i < 6 && p; i++) {
                    const btns = [...p.querySelectorAll('button')];
                    const addBtn = btns.find(b => b.innerText && (b.innerText.toLowerCase().includes('tambah') || b.innerText.toLowerCase().includes('add')));
                    if (addBtn) { addBtn.click(); return; }
                    p = p.parentElement;
                }
            }''')
        except Exception as e:
            print(f"DEBUG: Failed Produksi: {e}")
        await asyncio.sleep(2)"""
content = replace_block(content, old_prod, new_prod)

# Fix Penulis lagu
old_sw = """        try:
            field = self.page._page.locator(".semi-form-field").filter(has_text=re.compile(r"Songwriter|Penulis lagu", re.I)).first
            await field.locator("button").filter(has_text=re.compile(r"tambah|add", re.I)).click(force=True)
        except Exception as e:
            print(f"DEBUG: Failed Songwriter: {e}")
        await asyncio.sleep(2)"""
new_sw = """        try:
            await self.page._page.evaluate('''() => {
                const labels = [...document.querySelectorAll('div, span, label')];
                const target = labels.find(l => l.innerText && (l.innerText.toLowerCase() === 'penulis lagu' || l.innerText.toLowerCase() === 'songwriter'));
                if (!target) return;
                let p = target.parentElement;
                for (let i = 0; i < 6 && p; i++) {
                    const btns = [...p.querySelectorAll('button')];
                    const addBtn = btns.find(b => b.innerText && (b.innerText.toLowerCase().includes('tambah') || b.innerText.toLowerCase().includes('add')));
                    if (addBtn) { addBtn.click(); return; }
                    p = p.parentElement;
                }
            }''')
        except Exception as e:
            print(f"DEBUG: Failed Songwriter: {e}")
        await asyncio.sleep(2)"""
content = replace_block(content, old_sw, new_sw)

# Fix Konten Berlisensi
old_kb = """        try:
            field = self.page._page.locator(".semi-form-field").filter(has_text=re.compile(r"berlisensi|licensed", re.I)).first
            await field.locator("label").filter(has_text=re.compile(r"^Tidak$|^No$", re.I)).first.click(force=True)
        except Exception as e:
            print(f"DEBUG: Failed Konten Berlisensi: {e}")
        await asyncio.sleep(1)"""
new_kb = """        try:
            await self.page._page.evaluate('''() => {
                const labels = [...document.querySelectorAll('div, span, label')];
                const target = labels.find(l => l.innerText && (l.innerText.toLowerCase().includes('berlisensi') || l.innerText.toLowerCase().includes('licensed')));
                if (!target) return;
                let p = target.parentElement;
                for (let i = 0; i < 6 && p; i++) {
                    const radios = [...p.querySelectorAll('label')];
                    const noBtn = radios.find(r => r.innerText && (r.innerText.toLowerCase().trim() === 'tidak' || r.innerText.toLowerCase().trim() === 'no'));
                    if (noBtn) { noBtn.click(); return; }
                    p = p.parentElement;
                }
            }''')
        except Exception as e:
            print(f"DEBUG: Failed Konten Berlisensi: {e}")
        await asyncio.sleep(1)"""
content = replace_block(content, old_kb, new_kb)

# Fix Sudah Pernah Dirilis
old_spd = """        try:
            field = self.page._page.locator(".semi-form-field").filter(has_text=re.compile(r"pernah dirilis|previously released", re.I)).first
            await field.locator("label").filter(has_text=re.compile(r"Tidak|No", re.I)).first.click(force=True)
        except Exception as e:
            print(f"DEBUG: Failed Sudah Pernah Dirilis: {e}")
        await asyncio.sleep(1)"""
new_spd = """        try:
            await self.page._page.evaluate('''() => {
                const labels = [...document.querySelectorAll('div, span, label')];
                const target = labels.find(l => l.innerText && (l.innerText.toLowerCase().includes('pernah dirilis') || l.innerText.toLowerCase().includes('previously released')));
                if (!target) return;
                let p = target.parentElement;
                for (let i = 0; i < 6 && p; i++) {
                    const radios = [...p.querySelectorAll('label')];
                    const noBtn = radios.find(r => r.innerText && (r.innerText.toLowerCase().trim() === 'tidak' || r.innerText.toLowerCase().trim() === 'no'));
                    if (noBtn) { noBtn.click(); return; }
                    p = p.parentElement;
                }
            }''')
        except Exception as e:
            print(f"DEBUG: Failed Sudah Pernah Dirilis: {e}")
        await asyncio.sleep(1)"""
content = replace_block(content, old_spd, new_spd)

with open('src/pages/lagu_publish.py', 'w') as f:
    f.write(content)
